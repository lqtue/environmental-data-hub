#!/usr/bin/env python3
"""
compute_province_metrics.py

Computes province-level typhoon risk metrics for Vietnam (1995–present).

Source:
  - data/typhoon_landfalls.csv

Output:
  - data/province_metrics.csv

Run after process_landfall.py whenever the landfall dataset is updated.
"""

from pathlib import Path
import pandas as pd
import numpy as np

REPO_ROOT  = Path(__file__).parent.parent
INPUT_CSV  = REPO_ROOT / "data" / "typhoon_landfalls.csv"
OUTPUT_CSV = REPO_ROOT / "data" / "province_metrics.csv"


def main():
    print("Loading typhoon data...")
    df = pd.read_csv(INPUT_CSV)

    df['year'] = df['SID'].str[:4].astype(int)
    df_filtered = df[df['year'] >= 1995].copy()

    print(f"Total typhoon records: {len(df)}")
    print(f"Records from 1995-now: {len(df_filtered)} ({len(df_filtered)/len(df)*100:.1f}%)")
    print(f"Year range in filtered data: {df_filtered['year'].min()} - {df_filtered['year'].max()}")

    print("\n--- Calculating Province Metrics (1995-2025) ---")

    df_filtered['provinces_list'] = df_filtered['provinces_crossed'].str.split(', ')
    df_exploded = df_filtered.explode('provinces_list')

    province_stats = []

    for province in df_exploded['provinces_list'].unique():
        if pd.isna(province):
            continue

        direct = df_filtered[df_filtered['province_landfall'] == province]
        direct_count = len(direct)
        avg_wind = direct['wind_at_landfall_kph'].mean() if direct_count > 0 else 0

        crossed_count = len(df_exploded[df_exploded['provinces_list'] == province])

        if direct_count > 1:
            direct_sorted = direct.sort_values('calc_landfall_time')
            direct_sorted['landfall_dt'] = pd.to_datetime(direct_sorted['calc_landfall_time'])
            time_diffs = direct_sorted['landfall_dt'].diff().dt.total_seconds() / (24 * 3600)
            avg_days_between = time_diffs.mean()
        else:
            avg_days_between = np.nan

        province_stats.append({
            'Province': province,
            'Direct_Landfall_Count': direct_count,
            'Avg_Wind_at_Landfall_kph': round(avg_wind, 1),
            'Crossed_Count': crossed_count,
            'Avg_Days_Between_Landfalls': round(avg_days_between, 1) if not np.isnan(avg_days_between) else '',
        })

    df_province_metrics = pd.DataFrame(province_stats)
    df_province_metrics = df_province_metrics.sort_values('Direct_Landfall_Count', ascending=False)

    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    df_province_metrics.to_csv(OUTPUT_CSV, index=False)

    print(f"\nSaved to: {OUTPUT_CSV}")
    print(f"\nTop 10 provinces by Direct Landfall Count:")
    print(df_province_metrics.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
