#!/usr/bin/env python3
"""
prepare_dashboard_data.py

Prepares static data files for the typhoon dashboard:
  1. data/historical_tracks.geojson  — storm tracks for Vietnam-landfall storms
  2. data/province_metrics.json      — province-level risk metrics

Sources:
  - data/typhoon_landfalls.csv       (aggregated landfall data)
  - data/province_metrics.csv        (province-level metrics)

Run once whenever the IBTrACS dataset is updated.
"""

import csv
import json
import math
import zipfile
from collections import defaultdict
from pathlib import Path

import geopandas as gpd
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT        = Path(__file__).parent.parent
POINTS_ZIP  = ROOT / "TyphoonRaw" / "points.zip"
LANDFALL_CSV = ROOT / "data" / "typhoon_landfalls.csv"
PROVINCE_CSV = ROOT / "data" / "province_metrics.csv"
OUT_DIR     = ROOT / "data"
OUT_TRACKS  = OUT_DIR / "historical_tracks.geojson"
OUT_PROVINCE = OUT_DIR / "province_metrics.json"

# Bounding box for coordinate filtering (keep points in/near SCS + Vietnam corridor)
LON_MIN, LON_MAX = 95.0, 135.0
LAT_MIN, LAT_MAX = 5.0,  30.0

# ---------------------------------------------------------------------------
# Saffir-Simpson + JTWC category
# ---------------------------------------------------------------------------
def wind_category(wind_kt):
    """Vietnamese NCHMF classification (Quyết định 18/2021/QĐ-TTg)."""
    if wind_kt is None or math.isnan(wind_kt):
        return "unknown"
    w = float(wind_kt)
    if w < 21:  return "td"
    if w < 34:  return "td"
    if w < 48:  return "ts"
    if w < 64:  return "sts"
    if w < 100: return "ty"
    return "sty"

CAT_LABEL = {
    "td":  "Áp thấp nhiệt đới",
    "ts":  "Bão",
    "sts": "Bão mạnh",
    "ty":  "Bão rất mạnh",
    "sty": "Siêu bão",
    "unknown": "Không xác định",
}

# ---------------------------------------------------------------------------
# 1. Load IBTrACS points shapefile
# ---------------------------------------------------------------------------
print("Loading IBTrACS points shapefile...")
gdf = gpd.read_file(f"zip://{POINTS_ZIP}!IBTrACS.WP.list.v04r01.points.shp")
print(f"  Loaded {len(gdf):,} point records, {gdf['SID'].nunique():,} storms")

# Filter to Vietnam-relevant bounding box
gdf = gdf[
    (gdf.geometry.x >= LON_MIN) & (gdf.geometry.x <= LON_MAX) &
    (gdf.geometry.y >= LAT_MIN) & (gdf.geometry.y <= LAT_MAX)
].copy()
print(f"  After bbox filter: {len(gdf):,} points, {gdf['SID'].nunique():,} storms")

# ---------------------------------------------------------------------------
# 2. Load landfall data — get list of Vietnam-landfall SIDs + metadata
# ---------------------------------------------------------------------------
print("Loading landfall metadata...")
landfall_df = pd.read_csv(LANDFALL_CSV)
landfall_df["year"] = pd.to_datetime(landfall_df["calc_landfall_time"]).dt.year
landfall_sids = set(landfall_df["SID"].astype(str))

# Build metadata dict: SID → {name, year, wind_kph, province, time}
meta = {}
for _, row in landfall_df.iterrows():
    sid = str(row["SID"])
    if sid not in meta:
        meta[sid] = {
            "name":     str(row["NAME"]).strip(),
            "year":     int(row["year"]),
            "wind_kph": round(float(row["wind_at_landfall_kph"]), 1) if pd.notna(row["wind_at_landfall_kph"]) else 0,
            "wind_kt":  round(float(row["wind_at_landfall_kph"]) / 1.852, 1) if pd.notna(row["wind_at_landfall_kph"]) else 0,
            "province": str(row["province_landfall"]),
            "lat":      float(row["landfall_lat"]),
            "lon":      float(row["landfall_lon"]),
            "time":     str(row["calc_landfall_time"])[:16],
            "duration": round(float(row["time_on_land_h"]), 1) if pd.notna(row["time_on_land_h"]) else 0,
        }

print(f"  Vietnam-landfall SIDs: {len(landfall_sids)}")

# ---------------------------------------------------------------------------
# 3. Filter IBTrACS to Vietnam-landfall storms only
# ---------------------------------------------------------------------------
gdf_vn = gdf[gdf["SID"].isin(landfall_sids)].copy()
print(f"  Points for VN-landfall storms: {len(gdf_vn):,}")

# Parse time and wind
gdf_vn["ISO_TIME"] = pd.to_datetime(gdf_vn["ISO_TIME"], errors="coerce")
gdf_vn["USA_WIND"]  = pd.to_numeric(gdf_vn["USA_WIND"], errors="coerce")
gdf_vn["USA_PRES"]  = pd.to_numeric(gdf_vn["USA_PRES"], errors="coerce")

# Sort by storm, then time
gdf_vn = gdf_vn.sort_values(["SID", "ISO_TIME"])

# ---------------------------------------------------------------------------
# 4. Build GeoJSON LineString features (one per storm)
# ---------------------------------------------------------------------------
print("Building track GeoJSON...")
features = []

for sid, group in gdf_vn.groupby("SID"):
    coords = [
        [round(row.geometry.x, 4), round(row.geometry.y, 4)]
        for _, row in group.iterrows()
    ]
    if len(coords) < 2:
        continue

    m = meta.get(str(sid), {})
    name = m.get("name", "UNNAMED")
    year = m.get("year", 0)
    wind_kt = m.get("wind_kt", 0)
    cat = wind_category(wind_kt)

    # Also collect per-point wind data for segment coloring
    winds = [
        int(v) if pd.notna(v) else 0
        for v in group["USA_WIND"].tolist()
    ]
    times = [
        str(t)[:16] if pd.notna(t) else ""
        for t in group["ISO_TIME"].tolist()
    ]

    features.append({
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coords,
        },
        "properties": {
            "SID":          str(sid),
            "NAME":         name,
            "year":         year,
            "wind_kt":      wind_kt,
            "wind_kph":     m.get("wind_kph", 0),
            "category":     cat,
            "cat_label":    CAT_LABEL.get(cat, ""),
            "province":     m.get("province", ""),
            "landfall_lat": m.get("lat", 0),
            "landfall_lon": m.get("lon", 0),
            "landfall_time": m.get("time", ""),
            "duration_h":   m.get("duration", 0),
            # Per-point data for animated/segmented rendering
            "point_winds":  winds,
            "point_times":  times,
        },
    })

print(f"  Built {len(features)} storm track features")

# ---------------------------------------------------------------------------
# 5. Write historical_tracks.geojson
# ---------------------------------------------------------------------------
OUT_DIR.mkdir(exist_ok=True)
geojson = {
    "type": "FeatureCollection",
    "features": features,
    "_meta": {
        "source": "NOAA IBTrACS v04r01",
        "basin": "Western Pacific",
        "filter": "Vietnam mainland landfall storms only",
        "storm_count": len(features),
        "year_range": [
            int(min(m["year"] for m in meta.values() if m["year"] > 0)),
            int(max(m["year"] for m in meta.values() if m["year"] > 0)),
        ],
    },
}
OUT_TRACKS.write_text(json.dumps(geojson, ensure_ascii=False))
size_kb = OUT_TRACKS.stat().st_size / 1024
print(f"  ✓ Saved {OUT_TRACKS.name} ({size_kb:.0f} KB)")

# ---------------------------------------------------------------------------
# 6. Write province_metrics.json
# ---------------------------------------------------------------------------
print("Building province metrics JSON...")
pm_df = pd.read_csv(PROVINCE_CSV)
province_list = []
for _, row in pm_df.iterrows():
    avg_days = row["Avg_Days_Between_Landfalls"]
    province_list.append({
        "name":          str(row["Province"]),
        "landfall_count": int(row["Direct_Landfall_Count"]),
        "avg_wind_kph":  float(row["Avg_Wind_at_Landfall_kph"]),
        "crossed_count": int(row["Crossed_Count"]),
        "avg_days_between": round(float(avg_days), 1) if pd.notna(avg_days) else None,
    })

OUT_PROVINCE.write_text(json.dumps(province_list, ensure_ascii=False, indent=2))
print(f"  ✓ Saved {OUT_PROVINCE.name} ({len(province_list)} provinces)")

print("\nDone. Run a local server to test the dashboard:")
print("  cd", ROOT, "&& python3 -m http.server 8080")
