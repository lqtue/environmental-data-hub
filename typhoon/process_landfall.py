#!/usr/bin/env python3
"""
process_landfall.py

Processes IBTrACS Western Pacific point data to compute Vietnam typhoon
landfall statistics: times, positions, wind speeds, and provinces.

Sources:
  - TyphoonRaw/points.zip        (IBTrACS WP shapefile — points)
  - data/VietnamMainland.geojson
  - data/LandfallTyphoon.csv     (pre-filtered list of SIDs to process)
  - data/ProvincialMainland.geojson

Output:
  - data/typhoon_landfalls.csv

Run once whenever the IBTrACS dataset is updated.
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point
import numpy as np

REPO_ROOT = Path(__file__).parent.parent

PATH_POINTS   = f"zip://{REPO_ROOT / 'TyphoonRaw' / 'points.zip'}"  # lowercase — case-sensitive on Linux
PATH_MAINLAND = REPO_ROOT / "data" / "VietnamMainland.geojson"
PATH_FILTER_CSV = REPO_ROOT / "data" / "LandfallTyphoon.csv"
PATH_PROVINCES  = REPO_ROOT / "data" / "ProvincialMainland.geojson"
OUTPUT_CSV    = REPO_ROOT / "data" / "typhoon_landfalls.csv"

CRS_METRIC = 'EPSG:32648'
CRS_LATLON = 'EPSG:4326'


def get_start_point(geom):
    if geom.geom_type == 'LineString':
        return Point(geom.coords[0])
    elif geom.geom_type == 'MultiLineString':
        return Point(geom.geoms[0].coords[0])
    return None


def main():
    # ==========================================
    # 1. DATA LOADING & PREPARATION
    # ==========================================
    print("1. Loading Data...")

    target_sids = pd.read_csv(PATH_FILTER_CSV)['SID'].astype(str).unique()
    print(f"   - Found {len(target_sids)} storms to process.")

    cols = ['SID', 'NAME', 'ISO_TIME', 'USA_WIND', 'geometry']
    points = gpd.read_file(PATH_POINTS)[cols]
    points = points[points['SID'].isin(target_sids)].copy()

    mainland = gpd.read_file(PATH_MAINLAND).to_crs(CRS_METRIC)
    mainland_geom = mainland.dissolve()

    try:
        provinces = gpd.read_file(PATH_PROVINCES).to_crs(CRS_METRIC)
        has_provinces = True
    except Exception as e:
        print(f"   ! Warning: Province file not found or error ({e}). Skipping province details.")
        has_provinces = False

    # ==========================================
    # 2. UNIT CONVERSION
    # ==========================================
    print("2. Converting Units...")

    points['ISO_TIME'] = pd.to_datetime(points['ISO_TIME'])
    points['time_gmt7'] = (
        points['ISO_TIME']
        .dt.tz_localize('UTC')
        .dt.tz_convert(None)
        + pd.Timedelta(hours=7)
    )
    points['wind_kph'] = points['USA_WIND'].fillna(0) * 1.852
    points = points.to_crs(CRS_METRIC)

    # ==========================================
    # 3. SEGMENT CONSTRUCTION
    # ==========================================
    print("3. Building Track Segments...")

    points = points.sort_values(['SID', 'time_gmt7'])
    points['next_geom'] = points.groupby('SID')['geometry'].shift(-1)
    points['next_time'] = points.groupby('SID')['time_gmt7'].shift(-1)
    points['next_wind'] = points.groupby('SID')['wind_kph'].shift(-1)
    segments = points.dropna(subset=['next_geom']).copy()
    segments['geometry'] = segments.apply(lambda x: LineString([x['geometry'], x['next_geom']]), axis=1)
    segments = gpd.GeoDataFrame(segments, crs=CRS_METRIC)
    segments['seg_len_m'] = segments.length
    segments['seg_dur_h'] = (segments['next_time'] - segments['time_gmt7']).dt.total_seconds() / 3600

    # ==========================================
    # 4. GEOMETRIC INTERSECTION
    # ==========================================
    print("4. Calculating Mainland Intersections...")

    on_land = gpd.overlay(segments, mainland_geom, how='intersection')
    on_land['land_len_m'] = on_land.length
    on_land['ratio'] = on_land['land_len_m'] / on_land['seg_len_m']
    on_land['entry_offset_h'] = on_land['seg_dur_h'] * (1 - on_land['ratio'])
    on_land['calc_landfall_time'] = on_land['time_gmt7'] + pd.to_timedelta(on_land['entry_offset_h'], unit='h')
    on_land['time_on_land_h'] = on_land['seg_dur_h'] * on_land['ratio']
    on_land['avg_seg_wind'] = (on_land['wind_kph'] + on_land['next_wind']) / 2
    on_land['wind_x_time'] = on_land['avg_seg_wind'] * on_land['time_on_land_h']
    wind_diff = on_land['next_wind'] - on_land['wind_kph']
    on_land['landfall_wind_kph'] = on_land['wind_kph'] + (wind_diff * (1 - on_land['ratio']))

    # ==========================================
    # 5. PROVINCE IDENTIFICATION
    # ==========================================
    print("5. Identifying Provinces...")

    province_map = {}
    crossed_map = {}

    if has_provinces:
        relevant_segments = segments[segments['SID'].isin(on_land['SID'].unique())]
        joined = gpd.sjoin(relevant_segments, provinces, how='inner', predicate='intersects')
        crossed_map = joined.groupby('SID')['PROVINCE_NAME'].unique().apply(lambda x: ", ".join(list(x)))
        province_map = joined.sort_values('time_gmt7').groupby('SID')['PROVINCE_NAME'].first()
    else:
        print("   (Skipping province detail)")

    # ==========================================
    # 6. AGGREGATION & LAT/LON EXTRACTION
    # ==========================================
    print("6. Aggregating Final Stats...")

    final_stats = on_land.groupby('SID').agg({
        'NAME': 'first',
        'calc_landfall_time': 'min',
        'time_on_land_h': 'sum',
        'wind_x_time': 'sum',
    })
    final_stats['avg_wind_on_land_kph'] = final_stats['wind_x_time'] / final_stats['time_on_land_h']

    idx_min_rows = on_land.loc[on_land.groupby('SID')['calc_landfall_time'].idxmin()].set_index('SID')
    final_stats['wind_at_landfall_kph'] = idx_min_rows['landfall_wind_kph']

    landfall_geoms_metric = idx_min_rows['geometry'].apply(get_start_point)
    landfall_points_ll = gpd.GeoSeries(landfall_geoms_metric, crs=CRS_METRIC).to_crs(CRS_LATLON)
    final_stats['landfall_lat'] = landfall_points_ll.y
    final_stats['landfall_lon'] = landfall_points_ll.x

    if has_provinces:
        final_stats['province_landfall'] = province_map
        final_stats['provinces_crossed'] = crossed_map
    else:
        final_stats['province_landfall'] = "Vietnam (Mainland)"
        final_stats['provinces_crossed'] = "Vietnam (Mainland)"

    final_stats = final_stats.reset_index()
    final_stats = final_stats.sort_values('calc_landfall_time')
    final_stats['year'] = final_stats['calc_landfall_time'].dt.year
    final_stats['time_from_last_landfall_days'] = (
        final_stats.groupby('year')['calc_landfall_time'].diff().dt.total_seconds() / (3600 * 24)
    )
    final_stats['time_from_last_landfall_days'] = final_stats['time_from_last_landfall_days'].fillna(0)

    final_stats['wind_at_landfall_kph'] = final_stats['wind_at_landfall_kph'].round(1)
    final_stats['avg_wind_on_land_kph'] = final_stats['avg_wind_on_land_kph'].round(1)
    final_stats['time_on_land_h'] = final_stats['time_on_land_h'].round(1)
    final_stats['time_from_last_landfall_days'] = final_stats['time_from_last_landfall_days'].round(2)
    final_stats['landfall_lat'] = final_stats['landfall_lat'].round(4)
    final_stats['landfall_lon'] = final_stats['landfall_lon'].round(4)

    # ==========================================
    # 7. OUTPUT
    # ==========================================
    output_cols = [
        'SID', 'NAME',
        'calc_landfall_time',
        'landfall_lat', 'landfall_lon',
        'wind_at_landfall_kph',
        'province_landfall', 'provinces_crossed',
        'time_from_last_landfall_days',
        'time_on_land_h', 'avg_wind_on_land_kph',
    ]
    final_df = final_stats[[c for c in output_cols if c in final_stats.columns]]

    print("\nProcessing Complete.")
    print("Sample of first 5 rows:")
    print(final_df[['NAME', 'calc_landfall_time', 'landfall_lat', 'landfall_lon']].head())

    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nDone! Saved to '{OUTPUT_CSV}'")


if __name__ == "__main__":
    main()
