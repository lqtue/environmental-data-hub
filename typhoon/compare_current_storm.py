#!/usr/bin/env python3
"""
compare_current_storm.py

Analyzes a current typhoon (from JTWC KMZ) against historical IBTrACS
landfall data. Useful during an active event to provide context like:
  - How this storm compares to historical landfalls by wind speed
  - Which historical storms had similar tracks/intensity
  - Province-level risk based on forecast trajectory

Sources:
  - GeoJSON from kmz_to_geojson.py   (current storm)
  - data/typhoon_landfalls.csv        (historical landfalls)
  - data/VietnamMainland.geojson      (coastline for landfall detection)
  - data/ProvincialMainland.geojson   (province boundaries)

Usage:
  python scripts/compare_current_storm.py <storm.geojson> [--name "Tên bão số N"]

  The input GeoJSON must be the output of kmz_to_geojson.py.
  If --name is given, it overrides the storm name in the output.

Output:
  data/current_storm_analysis.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

REPO_ROOT = Path(__file__).parent.parent

PATH_LANDFALLS = REPO_ROOT / "data" / "typhoon_landfalls.csv"
PATH_MAINLAND  = REPO_ROOT / "data" / "VietnamMainland.geojson"
PATH_PROVINCES = REPO_ROOT / "data" / "ProvincialMainland.geojson"
OUTPUT_JSON    = REPO_ROOT / "data" / "current_storm_analysis.json"

CRS_METRIC = "EPSG:32648"
CRS_LATLON = "EPSG:4326"

# NCHMF classification (Quyết định 18/2021/QĐ-TTg)
def wind_category(wind_kt):
    if wind_kt < 21:  return "áp thấp"
    if wind_kt < 34:  return "áp thấp nhiệt đới"
    if wind_kt < 48:  return "bão"
    if wind_kt < 64:  return "bão mạnh"
    if wind_kt < 100: return "bão rất mạnh"
    return "siêu bão"


def knots_to_kmh(kt):
    return round(kt * 1.852, 1)


def load_current_storm(geojson_path: Path) -> dict:
    """Load kmz_to_geojson output and extract track data."""
    with open(geojson_path) as f:
        data = json.load(f)

    features = data["features"]
    meta = data.get("_meta", {})

    forecast_pts = [f for f in features if f["properties"]["feature_type"] == "forecast_point"]
    best_track_pts = [f for f in features if f["properties"]["feature_type"] == "best_track_point"]

    storm_name = meta.get("storm_name", "")
    if not storm_name and forecast_pts:
        storm_name = forecast_pts[0]["properties"].get("storm_name", "UNKNOWN")

    # Combine best track + forecast into a full track
    all_points = []

    for pt in best_track_pts:
        p = pt["properties"]
        coords = pt["geometry"]["coordinates"]
        all_points.append({
            "lon": coords[0], "lat": coords[1],
            "wind_kt": p["wind_kt"], "wind_kmh": p["wind_kmh"],
            "time_vn": p["time_vn"], "dtg_utc": p["dtg_utc"],
            "category": p["category"], "track_type": "observed",
        })

    for pt in forecast_pts:
        p = pt["properties"]
        coords = pt["geometry"]["coordinates"]
        all_points.append({
            "lon": coords[0], "lat": coords[1],
            "wind_kt": p["wind_kt"], "wind_kmh": p["wind_kmh"],
            "time_vn": p["time_vn"], "dtg_utc": p["dtg_utc"],
            "category": p["category"], "track_type": "forecast",
            "tau_h": p["tau_h"],
        })

    # Current position = first forecast point (TAU 0)
    current = forecast_pts[0]["properties"] if forecast_pts else {}
    current_coords = forecast_pts[0]["geometry"]["coordinates"] if forecast_pts else [0, 0]

    # Peak forecast wind
    max_fc = max(forecast_pts, key=lambda f: f["properties"]["wind_kt"]) if forecast_pts else None

    return {
        "storm_name": storm_name,
        "kmz_file": meta.get("kmz_file", ""),
        "current_position": {
            "lon": current_coords[0], "lat": current_coords[1],
            "wind_kt": current.get("wind_kt", 0),
            "wind_kmh": current.get("wind_kmh", 0),
            "category": current.get("category", ""),
            "time_vn": current.get("time_vn", ""),
        },
        "peak_forecast": {
            "wind_kt": max_fc["properties"]["wind_kt"],
            "wind_kmh": max_fc["properties"]["wind_kmh"],
            "category": max_fc["properties"]["category"],
            "tau_h": max_fc["properties"]["tau_h"],
            "time_vn": max_fc["properties"]["time_vn"],
        } if max_fc else None,
        "track_points": all_points,
        "forecast_count": len(forecast_pts),
        "best_track_count": len(best_track_pts),
    }


def estimate_landfall(storm: dict) -> dict | None:
    """Check if the forecast track crosses Vietnam mainland."""
    forecast_pts = [p for p in storm["track_points"] if p["track_type"] == "forecast"]
    if len(forecast_pts) < 2:
        return None

    try:
        mainland = gpd.read_file(PATH_MAINLAND).to_crs(CRS_METRIC)
        mainland_geom = mainland.dissolve().geometry.iloc[0]
    except Exception:
        return None

    try:
        provinces = gpd.read_file(PATH_PROVINCES).to_crs(CRS_METRIC)
    except Exception:
        provinces = None

    # Build forecast track segments
    for i in range(len(forecast_pts) - 1):
        p1 = forecast_pts[i]
        p2 = forecast_pts[i + 1]

        seg_ll = LineString([(p1["lon"], p1["lat"]), (p2["lon"], p2["lat"])])
        seg_gdf = gpd.GeoDataFrame(geometry=[seg_ll], crs=CRS_LATLON).to_crs(CRS_METRIC)
        seg_m = seg_gdf.geometry.iloc[0]

        if seg_m.intersects(mainland_geom):
            intersection = seg_m.intersection(mainland_geom)
            ratio = intersection.length / seg_m.length if seg_m.length > 0 else 0

            # Interpolate wind at landfall
            w1, w2 = p1["wind_kmh"], p2["wind_kmh"]
            landfall_wind = w1 + (w2 - w1) * (1 - ratio)
            landfall_wind_kt = p1["wind_kt"] + (p2["wind_kt"] - p1["wind_kt"]) * (1 - ratio)

            # Find province
            entry_pt_m = Point(seg_m.coords[0])
            province_name = None
            if provinces is not None:
                for _, prov in provinces.iterrows():
                    if prov.geometry.intersects(seg_m):
                        province_name = prov.get("PROVINCE_NAME", prov.get("NAME", ""))
                        break

            return {
                "estimated": True,
                "wind_kmh": round(landfall_wind, 1),
                "wind_kt": round(landfall_wind_kt, 1),
                "category": wind_category(landfall_wind_kt),
                "province": province_name,
                "between_tau": [p1.get("tau_h", "?"), p2.get("tau_h", "?")],
                "time_window": [p1["time_vn"], p2["time_vn"]],
            }

    return {"estimated": False, "note": "Dự báo không cho thấy bão đổ bộ Việt Nam"}


def compare_historical(storm: dict, landfall_est: dict | None) -> dict:
    """Compare current storm against historical landfalls."""
    df = pd.read_csv(PATH_LANDFALLS)

    # Filter to 1950+ for more reliable data
    df["year"] = df["SID"].str[:4].astype(int)
    df = df[df["year"] >= 1950].copy()

    total = len(df)

    result = {
        "total_historical_landfalls": total,
        "year_range": f"{df['year'].min()}–{df['year'].max()}",
    }

    # Current wind comparison
    current_wind = storm["current_position"]["wind_kmh"]
    peak_wind = storm["peak_forecast"]["wind_kmh"] if storm["peak_forecast"] else current_wind

    # How many historical storms were stronger at landfall?
    stronger = len(df[df["wind_at_landfall_kph"] > peak_wind])
    result["storms_stronger_at_landfall"] = stronger
    result["peak_forecast_percentile"] = round((1 - stronger / total) * 100, 1) if total > 0 else 0

    # Wind distribution
    result["historical_wind_stats"] = {
        "mean_kph": round(df["wind_at_landfall_kph"].mean(), 1),
        "median_kph": round(df["wind_at_landfall_kph"].median(), 1),
        "max_kph": round(df["wind_at_landfall_kph"].max(), 1),
        "p75_kph": round(df["wind_at_landfall_kph"].quantile(0.75), 1),
        "p90_kph": round(df["wind_at_landfall_kph"].quantile(0.90), 1),
    }

    # If we have province estimate, find historical landfalls there
    if landfall_est and landfall_est.get("estimated") and landfall_est.get("province"):
        prov = landfall_est["province"]
        prov_df = df[df["province_landfall"] == prov]
        result["province_history"] = {
            "province": prov,
            "landfall_count": len(prov_df),
            "avg_wind_kph": round(prov_df["wind_at_landfall_kph"].mean(), 1) if len(prov_df) > 0 else 0,
            "max_wind_kph": round(prov_df["wind_at_landfall_kph"].max(), 1) if len(prov_df) > 0 else 0,
            "last_landfall": prov_df["calc_landfall_time"].max() if len(prov_df) > 0 else None,
            "storms": prov_df[["NAME", "calc_landfall_time", "wind_at_landfall_kph"]].to_dict("records"),
        }

    # Find similar storms (within ±20 km/h of peak forecast)
    similar = df[
        (df["wind_at_landfall_kph"] >= peak_wind - 20) &
        (df["wind_at_landfall_kph"] <= peak_wind + 20)
    ].sort_values("wind_at_landfall_kph", ascending=False)

    result["similar_intensity_storms"] = similar[[
        "NAME", "calc_landfall_time", "wind_at_landfall_kph",
        "province_landfall", "time_on_land_h",
    ]].head(10).to_dict("records")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/compare_current_storm.py <storm.geojson> [--name \"Bão số N\"]")
        print("\n  storm.geojson = output of kmz_to_geojson.py")
        sys.exit(1)

    geojson_path = Path(sys.argv[1])
    if not geojson_path.exists():
        print(f"Error: {geojson_path} not found")
        sys.exit(1)

    # Parse optional --name
    custom_name = None
    if "--name" in sys.argv:
        idx = sys.argv.index("--name")
        if idx + 1 < len(sys.argv):
            custom_name = sys.argv[idx + 1]

    print(f"Loading {geojson_path.name}...")
    storm = load_current_storm(geojson_path)
    if custom_name:
        storm["storm_name"] = custom_name

    print(f"  Storm: {storm['storm_name']}")
    print(f"  Current: {storm['current_position']['wind_kt']} kt "
          f"({storm['current_position']['wind_kmh']} km/h) — "
          f"{storm['current_position']['category']}")
    if storm["peak_forecast"]:
        pf = storm["peak_forecast"]
        print(f"  Peak forecast: {pf['wind_kt']} kt ({pf['wind_kmh']} km/h) "
              f"at TAU {pf['tau_h']}h — {pf['category']}")

    print("\nEstimating landfall...")
    landfall = estimate_landfall(storm)
    if landfall and landfall.get("estimated"):
        print(f"  Forecast landfall: {landfall['category']} "
              f"({landfall['wind_kmh']} km/h)")
        print(f"  Province: {landfall['province'] or '(không xác định)'}")
        print(f"  Time window: {landfall['time_window'][0]} → {landfall['time_window'][1]}")
    else:
        print("  No Vietnam landfall detected in forecast")

    print("\nComparing against historical data...")
    comparison = compare_historical(storm, landfall)
    print(f"  Historical landfalls: {comparison['total_historical_landfalls']} "
          f"({comparison['year_range']})")
    print(f"  Peak forecast stronger than {comparison['peak_forecast_percentile']}% "
          f"of historical landfalls")
    print(f"  Similar storms (±20 km/h): {len(comparison['similar_intensity_storms'])}")

    # Assemble output
    output = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "storm": {
            "name": storm["storm_name"],
            "kmz_file": storm["kmz_file"],
            "current_position": storm["current_position"],
            "peak_forecast": storm["peak_forecast"],
            "track_points": storm["track_points"],
        },
        "landfall_estimate": landfall,
        "historical_comparison": comparison,
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"\nSaved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
