#!/usr/bin/env python3
"""
river_water.py — Crawl river water level data from VNDMS.

Sources:
  - Station lists: https://vndms.dmptc.gov.vn/water_level
  - Station detail: https://vndms.dmc.gov.vn/home/detailRain

Output: river_long.csv

Usage:
    python crawlers/river_water.py               # use default station list from config
    python crawlers/river_water.py --days 14     # fetch 14 days of history (default: 7)
    python crawlers/river_water.py --out river.csv
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import tz

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    ALLOWED_STATION_IDS,
    RIVER_DELAY,
    RIVER_DETAIL_URL,
    RIVER_HEADERS,
    RIVER_LIST_URL,
    RIVER_ALERT_LEVELS,
)

TZ_LOCAL = tz.gettz("Asia/Ho_Chi_Minh")
TZ_UTC   = tz.UTC

# Station ID extraction patterns (popup HTML from the list endpoint)
_SID_RE1 = re.compile(r"Mã trạm:\s*<b>(\d{3,})</b>", re.IGNORECASE)
_SID_RE2 = re.compile(r"detailrain\(`?(\d{3,})`?,\s*`?Water`?", re.IGNORECASE)
_SID_RE3 = re.compile(r"data-id=['\"](\d{3,})['\"]", re.IGNORECASE)


# ── Crawler helpers ───────────────────────────────────────────────────────────

def parse_station_id(popup_html: str) -> Optional[str]:
    if not popup_html:
        return None
    try:
        soup = BeautifulSoup(popup_html, "html.parser")
        el = soup.find(attrs={"class": "detalRain"})
        if el and el.has_attr("data-id"):
            return el["data-id"].strip()
        for li in soup.find_all("li"):
            if "Mã trạm" in li.get_text():
                m = re.search(r"(\d{3,})", li.get_text())
                if m:
                    return m.group(1)
    except Exception:
        pass
    for pat in (_SID_RE1, _SID_RE3, _SID_RE2):
        m = pat.search(popup_html)
        if m:
            return m.group(1)
    return None


def fetch_station_list(session: requests.Session, level: int) -> dict:
    r = session.get(RIVER_LIST_URL, params={"lv": str(level)}, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_station_detail(session: requests.Session, station_id: str, days: str = "7") -> Optional[dict]:
    data = {"id": station_id, "timeSelect": days, "source": "Water", "fromDate": "", "toDate": ""}
    r = session.post(RIVER_DETAIL_URL, data=data, timeout=30, headers=RIVER_HEADERS)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    try:
        return r.json()
    except json.JSONDecodeError:
        return json.loads(r.text.strip())


# ── Processing helpers ────────────────────────────────────────────────────────

def safe_floats(csv_str: Optional[str]) -> list:
    if not csv_str:
        return []
    out = []
    for x in csv_str.split(","):
        x = x.strip()
        try:
            out.append(float(x) if x not in ("", "-", "null", "NULL", "Null") else None)
        except ValueError:
            out.append(None)
    return out


def first_numeric(csv_str: Optional[str]) -> Optional[float]:
    for v in safe_floats(csv_str):
        if v is not None:
            return v
    return None


def parse_label_dt(label: str, year: int) -> Optional[datetime]:
    if not label:
        return None
    label = label.strip().replace("\n", "").replace("\\n", "")
    m = re.match(r"(\d{1,2})h(\d{1,2})/(\d{1,2})", label)
    if not m:
        return None
    hour, day, month = map(int, m.groups())
    try:
        return datetime(year, month, day, hour, tzinfo=TZ_LOCAL)
    except ValueError:
        return None


def classify_alert(level, bd1, bd2, bd3, hist) -> int:
    if level is None:
        return 0
    if hist is not None and not pd.isna(hist) and level >= hist:
        return 4
    if bd3 is not None and not pd.isna(bd3) and level >= bd3:
        return 3
    if bd2 is not None and not pd.isna(bd2) and level >= bd2:
        return 2
    if bd1 is not None and not pd.isna(bd1) and level >= bd1:
        return 1
    return 0


ALERT_NAMES = {
    0: "Bình thường", 1: "Trên BĐ1", 2: "Trên BĐ2",
    3: "Trên BĐ3",   4: "Trên lũ lịch sử",
}


def gap_cm(water_m, bd1, bd2, bd3, hist) -> Optional[float]:
    """Gap in cm between water level and relevant threshold (negative = below BĐ1)."""
    if pd.isna(water_m):
        return None
    for threshold in (hist, bd3, bd2, bd1):
        if threshold is not None and not pd.isna(threshold) and water_m >= threshold:
            return round((water_m - threshold) * 100)
    if bd1 is not None and not pd.isna(bd1):
        return round((water_m - bd1) * 100)
    return None


def m_to_cm(v) -> Optional[float]:
    return None if pd.isna(v) else round(float(v) * 100, 1)


def fmt_dt(dt) -> Optional[str]:
    return None if pd.isna(dt) else dt.strftime("%d/%m/%Y %H:%M")


# ── Main ─────────────────────────────────────────────────────────────────────

def crawl(days: str, out_path: Path, allowed_ids: set) -> None:
    session = requests.Session()
    session.headers.update(RIVER_HEADERS)

    # Collect station metadata from all alert levels
    seen = {}
    print(f"Fetching station lists for levels {RIVER_ALERT_LEVELS}...")
    for lv in RIVER_ALERT_LEVELS:
        try:
            fc = fetch_station_list(session, int(lv))
        except Exception as e:
            print(f"  [WARN] list level {lv}: {e}")
            continue
        for f in (fc or {}).get("features", []):
            props = f.get("properties", {}) or {}
            geom  = f.get("geometry", {}) or {}
            coords = geom.get("coordinates") or [None, None]
            x = y = None
            if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                x, y = float(coords[0]), float(coords[1])
            popup = props.get("popupInfo") or ""
            province = None
            try:
                soup = BeautifulSoup(popup, "html.parser")
                for li in soup.find_all("li"):
                    text = li.get_text(" ", strip=True)
                    if text.lower().startswith("địa điểm:"):
                        province = re.sub(r"^Địa điểm:\s*", "", text, flags=re.IGNORECASE).strip()
                        break
            except Exception:
                pass
            sid = parse_station_id(popup)
            if sid:
                meta = seen.setdefault(sid, {
                    "station_id": sid, "label": props.get("label"),
                    "province_from_popup": province, "x": x, "y": y,
                    "max_alert_seen": int(lv),
                })
                meta["max_alert_seen"] = max(meta["max_alert_seen"], int(lv))

    print(f"Found {len(seen)} unique stations.")

    targets = {sid: m for sid, m in seen.items() if sid in allowed_ids} if allowed_ids else seen
    missing = allowed_ids - set(seen.keys())
    if missing:
        print(f"  [WARN] Not found in station lists: {missing}")
    print(f"Fetching details for {len(targets)} station(s)...")

    station_details = {}
    stations_meta   = {}
    for sid, meta in targets.items():
        try:
            detail = fetch_station_detail(session, sid, days=days)
        except Exception as e:
            print(f"  [WARN] detail fetch for {sid}: {e}")
            detail = None
        if isinstance(detail, dict):
            hist_str = detail.get("gia_tri_lu_lich_su")
            meta["historical_flood_year"]  = detail.get("nam_lu_lich_su")
            meta["historical_flood_value"] = None
            if hist_str:
                try:
                    val = float(hist_str.split(",")[0])
                    if val > 0:
                        meta["historical_flood_value"] = val
                except (ValueError, IndexError):
                    pass
        station_details[sid] = detail
        stations_meta[sid]   = meta
        time.sleep(RIVER_DELAY)

    # ── Process into long-format rows ─────────────────────────────────────────
    assume_year = datetime.now(TZ_LOCAL).year
    rows = []
    for sid, detail in station_details.items():
        if not isinstance(detail, dict):
            continue
        meta    = stations_meta.get(sid, {})
        name    = detail.get("name_vn")
        river   = detail.get("river_name")
        province = detail.get("province_name") or meta.get("province_from_popup")
        x, y    = meta.get("x"), meta.get("y")
        labels  = (detail.get("labels") or "").split(",")
        values  = safe_floats(detail.get("value"))
        bd1 = first_numeric(detail.get("bao_dong1"))
        bd2 = first_numeric(detail.get("bao_dong2"))
        bd3 = first_numeric(detail.get("bao_dong3"))
        hist_val  = meta.get("historical_flood_value")
        hist_year = meta.get("historical_flood_year")
        if hist_val is not None and hist_val <= 0:
            hist_val = None

        n = min(len(labels), len(values))
        for i in range(n):
            dt_obj = parse_label_dt(labels[i], assume_year)
            if not dt_obj:
                continue
            wl = values[i]
            alert_v = classify_alert(wl, bd1, bd2, bd3, hist_val)
            rows.append({
                "station_id": sid, "name": name, "river": river, "province": province,
                "dt": dt_obj, "water_level_m": wl,
                "bd1_m": bd1, "bd2_m": bd2, "bd3_m": bd3,
                "history_flood_m": hist_val, "history_flood_year": hist_year,
                "alert_value": alert_v,
                "gap_cm_calc": gap_cm(wl, bd1, bd2, bd3, hist_val) if wl is not None else None,
                "x": x, "y": y,
            })

    if not rows:
        print("No rows processed.")
        return

    df = pd.DataFrame(rows)
    df = df[df["dt"].notna()].copy()
    df["date_only"] = df["dt"].dt.date

    # Dynamic time filter: last N days up to now
    now_gmt7 = datetime.now(TZ_LOCAL)
    end_filter   = now_gmt7.replace(minute=0, second=0, microsecond=0)
    start_filter = (df["dt"].max().date() - pd.Timedelta(days=int(days))) if not df.empty else now_gmt7.date() - pd.Timedelta(days=int(days))

    df = df[(df["date_only"] >= start_filter) & (df["dt"] <= end_filter)].copy()
    if df.empty:
        print("No rows after date filtering.")
        return

    df.sort_values(["station_id", "dt"], inplace=True)
    df["start_dt"] = df.groupby("station_id")["dt"].shift(1).fillna(df["dt"])

    df_out = pd.DataFrame({
        "Mã trạm":       df["station_id"],
        "Trạm":          df["name"],
        "Tên tỉnh":      df["province"],
        "Tên sông":      df["river"],
        "Mực nước (cm)": df["water_level_m"].apply(m_to_cm),
        "Cảnh báo":      df["alert_value"].map(ALERT_NAMES),
        "Chênh lệch (cm)": df["gap_cm_calc"],
        "Cảnh báo value (0-4)": df["alert_value"],
        "BĐ1 (m)": df["bd1_m"], "BĐ2 (m)": df["bd2_m"], "BĐ3 (m)": df["bd3_m"],
        "Mực nước lịch sử (m)": df["history_flood_m"],
        "Năm lũ lịch sử": df["history_flood_year"],
        "Thời gian (GMT+7)":    df["dt"].apply(fmt_dt),
        "Start time (GMT+7)":   df["start_dt"].apply(fmt_dt),
        "End time (GMT+7)":     df["dt"].apply(fmt_dt),
        "x": df["x"], "y": df["y"],
    })

    # Append "No Data" rows for stations with reporting gaps
    global_end = df["dt"].max()
    last_rows  = df.loc[df.groupby("station_id")["dt"].idxmax()]
    gaps = last_rows[last_rows["dt"] < global_end]
    gap_records = []
    for _, lr in gaps.iterrows():
        gap_records.append({
            "Mã trạm": lr["station_id"], "Trạm": lr["name"],
            "Tên tỉnh": lr["province"],  "Tên sông": lr["river"],
            "Mực nước (cm)": np.nan, "Cảnh báo": "Không có dữ liệu",
            "Chênh lệch (cm)": np.nan, "Cảnh báo value (0-4)": np.nan,
            "BĐ1 (m)": lr["bd1_m"], "BĐ2 (m)": lr["bd2_m"], "BĐ3 (m)": lr["bd3_m"],
            "Mực nước lịch sử (m)": lr["history_flood_m"],
            "Năm lũ lịch sử": lr["history_flood_year"],
            "Thời gian (GMT+7)": fmt_dt(global_end),
            "Start time (GMT+7)": fmt_dt(lr["dt"]),
            "End time (GMT+7)": fmt_dt(global_end),
            "x": lr["x"], "y": lr["y"],
        })
    if gap_records:
        df_out = pd.concat([df_out, pd.DataFrame(gap_records)], ignore_index=True)

    df_out.sort_values(["Mã trạm", "Start time (GMT+7)"], inplace=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✓ {len(df_out)} rows → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Crawl river water levels from VNDMS")
    parser.add_argument("--days", default="7", help="Days of history to fetch (default: 7)")
    parser.add_argument("--out",  default="river_long.csv", help="Output CSV path")
    args = parser.parse_args()
    crawl(args.days, Path(args.out), ALLOWED_STATION_IDS)


if __name__ == "__main__":
    main()
