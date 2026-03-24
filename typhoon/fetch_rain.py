#!/usr/bin/env python3
"""
fetch_rain.py

Fetches NASA POWER precipitation data for Vietnam and computes rain anomaly
polygons compared to the 30-year climatological normal.

Sources:
  - NASA POWER API (https://power.larc.nasa.gov/)
  - CountryBoundary.geojson  — MUST be supplied manually (not in repo)

Output:
  - rain/RainAnomaly.geojson

Usage:
  1. Place CountryBoundary.geojson in the repo root.
  2. pip install geopandas pandas numpy requests scipy matplotlib shapely
  3. python scripts/fetch_rain.py [YYYYMMDD start] [YYYYMMDD end]

  Examples:
    python scripts/fetch_rain.py                     # defaults to Jan 1 – Nov 30 of current year
    python scripts/fetch_rain.py 20260901 20261115   # Sep 1 – Nov 15, 2026
"""

import sys
from pathlib import Path
from datetime import datetime
import geopandas as gpd
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import concurrent.futures
import warnings
from scipy.interpolate import griddata
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union

REPO_ROOT = Path(__file__).parent.parent

# NOTE: CountryBoundary.geojson is NOT tracked in this repo.
# Download or export the Vietnam country boundary shapefile and place it here.
BOUNDARY_FILE = REPO_ROOT / "CountryBoundary.geojson"
OUTPUT_FILE   = REPO_ROOT / "rain" / "RainAnomaly.geojson"

FETCH_RES  = 0.5   # NASA resolution (~50 km)
INTERP_RES = 0.05  # Output resolution (~5 km)

# Month names used by NASA POWER climatology API
_MONTH_KEYS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
               'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

warnings.filterwarnings("ignore", category=DeprecationWarning)


def _month_range(start_date: str, end_date: str) -> list[int]:
    """Return list of 0-based month indices covered by date range (YYYYMMDD)."""
    m0 = int(start_date[4:6]) - 1   # e.g. "01" → 0
    m1 = int(end_date[4:6]) - 1     # e.g. "11" → 10
    return list(range(m0, m1 + 1))


def fetch_point(args):
    idx, geom, start_date, end_date, months = args
    lat, lon = geom.y, geom.x
    try:
        with requests.Session() as s:
            r1 = s.get("https://power.larc.nasa.gov/api/temporal/daily/point", params={
                "parameters": "PRECTOTCORR", "community": "AG",
                "latitude": lat, "longitude": lon,
                "start": start_date, "end": end_date, "format": "JSON",
            }, timeout=30).json()

            r2 = s.get("https://power.larc.nasa.gov/api/temporal/climatology/point", params={
                "parameters": "PRECTOTCORR", "community": "AG",
                "latitude": lat, "longitude": lon, "format": "JSON",
            }, timeout=30).json()

        d_vals = r1['properties']['parameter']['PRECTOTCORR']
        rain_actual = sum(v for v in d_vals.values() if v >= 0)

        c_vals = r2['properties']['parameter']['PRECTOTCORR']
        rain_norm = sum(
            c_vals.get(_MONTH_KEYS[m], 0) * _MONTH_DAYS[m]
            for m in months
            if c_vals.get(_MONTH_KEYS[m], -99) >= 0
        )

        if rain_norm > 0:
            anom = ((rain_actual - rain_norm) / rain_norm) * 100
            return [lon, lat, anom, rain_actual, rain_norm]
    except Exception:
        return None
    return None


def smooth_grid(points, vals, gx, gy):
    g = griddata(points, vals, (gx, gy), method='cubic')
    mask = np.isnan(g)
    if mask.any():
        g[mask] = griddata(points, vals, (gx[mask], gy[mask]), method='nearest')
    return g


def main():
    # Parse CLI args: python fetch_rain.py [START_DATE] [END_DATE]
    if len(sys.argv) >= 3:
        start_date = sys.argv[1]
        end_date   = sys.argv[2]
    elif len(sys.argv) == 2:
        print("Usage: python scripts/fetch_rain.py <YYYYMMDD start> <YYYYMMDD end>")
        sys.exit(1)
    else:
        # Default: Jan 1 to Nov 30 of current year
        year = datetime.now().year
        start_date = f"{year}0101"
        end_date   = f"{year}1130"

    months = _month_range(start_date, end_date)
    print(f"Date range: {start_date} → {end_date} ({len(months)} months)")

    if not BOUNDARY_FILE.exists():
        raise FileNotFoundError(
            f"CountryBoundary.geojson not found at {BOUNDARY_FILE}. "
            "Download or export the Vietnam boundary file and place it in the repo root."
        )

    print("1. Loading Boundary & Preparing Grid...")
    gdf_boundary = gpd.read_file(BOUNDARY_FILE)
    gdf_boundary['geometry'] = gdf_boundary.geometry.buffer(0)
    bounds = gdf_boundary.total_bounds

    x_range = np.arange(bounds[0] - 0.5, bounds[2] + 0.5, FETCH_RES)
    y_range = np.arange(bounds[1] - 0.5, bounds[3] + 0.5, FETCH_RES)
    temp_points = [Point(x, y) for x in x_range for y in y_range]
    gdf_temp = gpd.GeoDataFrame(geometry=temp_points, crs=gdf_boundary.crs)
    gdf_target = gpd.sjoin(gdf_temp, gdf_boundary.buffer(1.0).to_frame('geometry'), how="inner")
    total_pts = len(gdf_target)
    print(f"   -> Grid ready: {total_pts} points.")

    print("2. Starting Parallel Download (10 Workers)...")
    data_list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(fetch_point, (idx, row.geometry, start_date, end_date, months))
            for idx, row in gdf_target.iterrows()
        ]
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            if res:
                data_list.append(res)
            if i % 10 == 0:
                print(f"      Progress: {i}/{total_pts}...", end="\r")

    print(f"\n   -> Download Complete! Valid Points: {len(data_list)}")
    data_arr = np.array(data_list)
    pts      = data_arr[:, 0:2]
    v_anom   = data_arr[:, 2]
    v_2025   = data_arr[:, 3]
    v_norm   = data_arr[:, 4]

    print("3. Interpolating with Edge Filling...")
    pad = 0.5
    gx, gy = np.mgrid[bounds[0] - pad:bounds[2] + pad:INTERP_RES,
                      bounds[1] - pad:bounds[3] + pad:INTERP_RES]
    g_anom = smooth_grid(pts, v_anom, gx, gy)
    g_2025 = smooth_grid(pts, v_2025, gx, gy)
    g_norm = smooth_grid(pts, v_norm, gx, gy)

    print("4. Generating Polygons (Cookie Cutter Method)...")
    d_min, d_max = np.min(g_anom), np.max(g_anom)
    levels = np.arange(np.floor(d_min / 10) * 10, np.ceil(d_max / 10) * 10 + 10, 10)

    fig, ax = plt.subplots()
    contour = ax.contourf(gx, gy, g_anom, levels=levels)
    plt.close(fig)

    level_geoms = {}
    for i, collection in enumerate(contour.collections):
        polys = []
        for path in collection.get_paths():
            for coords in path.to_polygons():
                if len(coords) < 3:
                    continue
                p = Polygon(coords)
                if not p.is_valid:
                    p = p.buffer(0)
                polys.append(p)
        if polys:
            level_geoms[i] = unary_union(polys)

    final_features = []
    sorted_levels = sorted(level_geoms.keys())
    for i in sorted_levels:
        if i == len(levels) - 1:
            continue
        current_geom = level_geoms[i]
        min_v, max_v = levels[i], levels[i + 1]
        higher_geoms = [level_geoms[j] for j in sorted_levels if j > i]
        if higher_geoms:
            higher_shape = unary_union(higher_geoms)
            if not higher_shape.is_valid:
                higher_shape = higher_shape.buffer(0)
            current_geom = current_geom.difference(higher_shape)
        if not current_geom.is_empty:
            mask_zone = (g_anom >= min_v) & (g_anom < max_v)
            m_2025 = np.nanmean(g_2025[mask_zone]) if np.any(mask_zone) else 0
            m_norm = np.nanmean(g_norm[mask_zone]) if np.any(mask_zone) else 0
            final_features.append({
                'geometry': current_geom,
                'Anomaly_Min': float(min_v),
                'Anomaly_Max': float(max_v),
                'Avg_Rain_2025': float(round(m_2025, 0)),
                'Avg_Rain_Normal': float(round(m_norm, 0)),
                'Abs_Anomaly': float(abs((min_v + max_v) / 2)),
                'Label': f"{int(min_v)}% to {int(max_v)}%",
            })

    print("5. Clipping to Vietnam...")
    gdf_raw = gpd.GeoDataFrame(final_features, crs=gdf_boundary.crs)
    gdf_raw['geometry'] = gdf_raw.geometry.buffer(0)
    try:
        gdf_final = gpd.clip(gdf_raw, gdf_boundary)
    except Exception:
        print("   ! Clip failed, using fallback intersection...")
        gdf_final = gpd.overlay(gdf_raw, gdf_boundary, how='intersection')

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    gdf_final.to_file(OUTPUT_FILE, driver="GeoJSON")
    print(f"\nSUCCESS! Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
