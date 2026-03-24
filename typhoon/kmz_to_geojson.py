#!/usr/bin/env python3
"""
kmz_to_geojson.py

Converts a JTWC typhoon warning KMZ file to GeoJSON.

Extracts 4 feature types:
  1. forecast_point   — forecast track positions (Point)
  2. wind_radii       — 34/50/64 kt wind radii polygons (Polygon)
  3. best_track_point — historical best-track positions (Point)
  4. track_line       — forecast + best-track LineStrings

All times converted from UTC to GMT+7 and formatted as Vietnamese
date strings (e.g. "T3, 17/3" = Tuesday 17 March, "T3, 17/3 19:00" with hour).
Wind speeds converted from knots to km/h.

Usage:
  python scripts/kmz_to_geojson.py <input.kmz> [output.geojson]

  If output path is omitted, writes to data/<storm_id>.geojson
"""

import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
NS = "http://www.opengis.net/kml/2.2"

VN_WEEKDAY = {0: "T2", 1: "T3", 2: "T4", 3: "T5", 4: "T6", 5: "T7", 6: "CN"}
VN_TZ = timezone(timedelta(hours=7))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def knots_to_kmh(kt: float) -> float:
    return round(kt * 1.852, 1)


def vn_datetime(dt_utc: datetime, include_time: bool = True) -> str:
    """Format a UTC datetime as Vietnamese 'T3, 17/3' or 'T3, 17/3 19:00'."""
    dt_vn = dt_utc.astimezone(VN_TZ)
    day_str = VN_WEEKDAY[dt_vn.weekday()]
    date_str = f"{dt_vn.day}/{dt_vn.month}"
    if include_time:
        return f"{day_str}, {date_str} {dt_vn.strftime('%H:%M')}"
    return f"{day_str}, {date_str}"


def parse_dtg_from_desc(desc: str) -> datetime | None:
    """Extract full UTC datetime from description HTML (e.g. 2026031800Z)."""
    m = re.search(r"(\d{10})Z", desc)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y%m%d%H").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def parse_best_track_dtg(name: str) -> datetime | None:
    """Parse best-track placemark name like '26031412Z' → UTC datetime."""
    m = re.match(r"^(\d{8})Z$", name.strip())
    if m:
        try:
            return datetime.strptime("20" + m.group(1), "%Y%m%d%H").replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def wind_category(wind_kt: float) -> str:
    """Vietnamese NCHMF classification (Quyết định 18/2021/QĐ-TTg)."""
    if wind_kt < 21:
        return "áp thấp"
    if wind_kt < 34:
        return "áp thấp nhiệt đới"
    if wind_kt < 48:
        return "bão"
    if wind_kt < 64:
        return "bão mạnh"
    if wind_kt < 100:
        return "bão rất mạnh"
    return "siêu bão"


FEATURE_NAME_VN = {
    "forecast_point":  "Vị trí dự báo",
    "wind_radii":      "Vùng gió",
    "best_track_point": "Vị trí theo dõi",
    "forecast_track":  "Đường dự báo",
    "best_track":      "Đường đi thực tế",
    "danger_swath":    "Vùng nguy hiểm",
}


def parse_coords(text: str) -> list[list[float]]:
    """Parse KML coordinates string → [[lon, lat], ...]"""
    pts = []
    for token in text.strip().split():
        parts = token.split(",")
        if len(parts) >= 2:
            pts.append([float(parts[0]), float(parts[1])])
    return pts


def find_text(el, tag: str) -> str:
    found = el.find(f"{{{NS}}}{tag}")
    return found.text.strip() if found is not None and found.text else ""


# ---------------------------------------------------------------------------
# Forecast name parsers
# ---------------------------------------------------------------------------

# "17/00Z (TROPICAL CYCLONE 27P (TWENTYSEVEN) WARNING NR 1 - 40 knots)"
_FC_FIRST = re.compile(r"^(\d{1,2})/(\d{2})Z\b.*?-\s*(\d+)\s*knots\)?", re.IGNORECASE)
# "17/12Z - 50 knots"
_FC_REST  = re.compile(r"^(\d{1,2})/(\d{2})Z\s+-\s+(\d+)\s*knots", re.IGNORECASE)
# "RADIUS OF 34 KT WINDS"
_RADII    = re.compile(r"RADIUS OF (\d+) KT WINDS", re.IGNORECASE)
# Best track DTG: 26031412Z (YYMMDDHHz)
_BTK_DTG  = re.compile(r"^(\d{8})Z$")


def _parse_forecast_name(name: str):
    """Return (day, hour, wind_kt) or None."""
    for pattern in (_FC_FIRST, _FC_REST):
        m = pattern.match(name.strip())
        if m:
            return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


# ---------------------------------------------------------------------------
# KML parsing
# ---------------------------------------------------------------------------

def parse_kml(kml_text: str) -> dict:
    """
    Parse JTWC KML and return a dict of extracted data:
      {
        "storm_name": str,
        "storm_id": str,
        "forecast_points": [...],
        "wind_radii": [...],
        "best_track_points": [...],
        "track_lines": [...],
      }
    """
    root = ET.fromstring(kml_text)

    # Storm metadata from root Document name
    doc_name = root.findtext(f".//{{{NS}}}Document/{{{NS}}}name", "").strip()

    # Collect all placemarks in document order
    placemarks = root.findall(f".//{{{NS}}}Placemark")

    forecast_points = []
    wind_radii      = []
    best_track_pts  = []
    track_lines     = []

    storm_name = ""
    storm_id   = ""

    # Reference month/year: derive from first forecast point description
    ref_year  = None
    ref_month = None

    # We'll do two passes: first to get ref year/month, then to parse all
    for pm in placemarks:
        desc = find_text(pm, "description")
        dt = parse_dtg_from_desc(desc)
        if dt and ref_year is None:
            ref_year  = dt.year
            ref_month = dt.month
            # Storm name: value cell after NAME header in HTML table
            # <tr><td><B>NAME</B></td><td><B>TWENTYSEVE</B></td></tr>
            m = re.search(r"<B>NAME</B>.*?<B>([\w\s]+)</B>", desc, re.DOTALL)
            if m:
                storm_name = m.group(1).strip()
            break

    # Fallback: derive year/month from best track DTGs
    if ref_year is None:
        for pm in placemarks:
            name = find_text(pm, "name")
            dt = parse_best_track_dtg(name)
            if dt:
                ref_year  = dt.year
                ref_month = dt.month
                break

    if ref_year is None:
        ref_year  = datetime.now(timezone.utc).year
        ref_month = datetime.now(timezone.utc).month

    def day_hour_to_dt(day: int, hour: int) -> datetime:
        """Resolve day/hour (UTC) to full datetime using ref month/year."""
        month = ref_month
        year  = ref_year
        # Handle month rollover (e.g. forecast crosses into next month)
        try:
            return datetime(year, month, day, hour, tzinfo=timezone.utc)
        except ValueError:
            # Try next month
            month = month % 12 + 1
            if month == 1:
                year += 1
            return datetime(year, month, day, hour, tzinfo=timezone.utc)

    # Warning reference time: the first forecast point is TAU 0 (current position)
    warning_dt = None

    # Current wind-radii context: tie radii to the last forecast time seen
    current_fc_dt   = None
    current_fc_tau  = None

    for pm in placemarks:
        name = find_text(pm, "name")
        desc = find_text(pm, "description")

        # --- Forecast point ---
        parsed = _parse_forecast_name(name)
        if parsed:
            day, hour, wind_kt = parsed
            dt_utc = parse_dtg_from_desc(desc) or day_hour_to_dt(day, hour)
            current_fc_dt  = dt_utc

            # TAU from description, or derive from warning_dt
            tau_m = re.search(r"TAU\s+(\d+)", desc)
            if tau_m:
                current_fc_tau = int(tau_m.group(1))
            elif warning_dt:
                current_fc_tau = int((dt_utc - warning_dt).total_seconds() / 3600)
            else:
                current_fc_tau = 0  # first point is current position (TAU 0)

            # Set warning_dt on first forecast point (TAU 0)
            if warning_dt is None:
                warning_dt = dt_utc

            # Storm name from description (if not already found)
            if not storm_name:
                m = re.search(r"<B>NAME</B>.*?<B>([\w\s]+)</B>", desc, re.DOTALL)
                if m:
                    storm_name = m.group(1).strip()

            # Movement
            mov_deg = mov_kmh = None
            mov_m = re.search(r"(\d+)\s*DEG AT\s*([\d.]+)\s*KT", desc, re.IGNORECASE)
            if mov_m:
                mov_deg  = int(mov_m.group(1))
                mov_kmh  = knots_to_kmh(float(mov_m.group(2)))

            coords_el = pm.find(f".//{{{NS}}}coordinates")
            if coords_el is None:
                continue
            lon, lat = parse_coords(coords_el.text)[0]

            forecast_points.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "feature_type":  "forecast_point",
                    "feature_name_vn": FEATURE_NAME_VN["forecast_point"],
                    "storm_name":    storm_name,
                    "tau_h":         current_fc_tau,
                    "dtg_utc":       dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "time_vn":       vn_datetime(dt_utc),
                    "wind_kt":       wind_kt,
                    "wind_kmh":      knots_to_kmh(wind_kt),
                    "category":      wind_category(wind_kt),
                    "movement_deg":  mov_deg,
                    "movement_kmh":  mov_kmh,
                },
            })
            continue

        # --- Wind radii polygon ---
        radii_m = _RADII.match(name)
        if radii_m:
            radii_kt = int(radii_m.group(1))
            coords_el = pm.find(f".//{{{NS}}}coordinates")
            if coords_el is None:
                continue
            pts = parse_coords(coords_el.text)
            if pts and pts[0] != pts[-1]:
                pts.append(pts[0])  # close ring

            wind_radii.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [pts]},
                "properties": {
                    "feature_type": "wind_radii",
                    "feature_name_vn": FEATURE_NAME_VN["wind_radii"],
                    "radii_kt":     radii_kt,
                    "radii_kmh":    knots_to_kmh(radii_kt),
                    "tau_h":        current_fc_tau,
                    "dtg_utc":      current_fc_dt.strftime("%Y-%m-%dT%H:%M:%SZ") if current_fc_dt else None,
                    "time_vn":      vn_datetime(current_fc_dt) if current_fc_dt else None,
                },
            })
            continue

        # --- Best track point ---
        btk_dt = parse_best_track_dtg(name)
        if btk_dt:
            wind_m = re.search(r"(\d+)\s*knots", desc, re.IGNORECASE)
            wind_kt = int(wind_m.group(1)) if wind_m else 0
            coords_el = pm.find(f".//{{{NS}}}coordinates")
            if coords_el is None:
                continue
            lon, lat = parse_coords(coords_el.text)[0]

            best_track_pts.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": {
                    "feature_type": "best_track_point",
                    "feature_name_vn": FEATURE_NAME_VN["best_track_point"],
                    "dtg_utc":      btk_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "time_vn":      vn_datetime(btk_dt),
                    "wind_kt":      wind_kt,
                    "wind_kmh":     knots_to_kmh(wind_kt),
                    "category":     wind_category(wind_kt),
                },
            })
            continue

        # --- Track lines and danger swath ---
        ls_el  = pm.find(f".//{{{NS}}}LineString")
        pol_el = pm.find(f".//{{{NS}}}Polygon")

        if ls_el is not None:
            coords_el = ls_el.find(f".//{{{NS}}}coordinates")
            if coords_el is None:
                continue
            pts = parse_coords(coords_el.text)
            ftype = "best_track" if "Best Track" in name else "forecast_track"
            track_lines.append({
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": pts},
                "properties": {
                    "feature_type": ftype,
                    "feature_name_vn": FEATURE_NAME_VN[ftype],
                    "name":         name,
                },
            })

        elif pol_el is not None:
            coords_el = pol_el.find(f".//{{{NS}}}coordinates")
            if coords_el is None:
                continue
            pts = parse_coords(coords_el.text)
            if pts and pts[0] != pts[-1]:
                pts.append(pts[0])
            track_lines.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [pts]},
                "properties": {
                    "feature_type": "danger_swath",
                    "feature_name_vn": FEATURE_NAME_VN["danger_swath"],
                    "name":         name,
                    "radii_kt":     34,
                    "radii_kmh":    knots_to_kmh(34),
                },
            })

    # Derive storm_id from KMZ filename context (set by caller)
    return {
        "storm_name":       storm_name,
        "forecast_points":  forecast_points,
        "wind_radii":       wind_radii,
        "best_track_points": best_track_pts,
        "track_lines":      track_lines,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def convert(kmz_path: Path, output_path: Path) -> None:
    print(f"Reading {kmz_path.name}...")

    with zipfile.ZipFile(kmz_path) as zf:
        kml_name = next(n for n in zf.namelist() if n.endswith(".kml"))
        kml_text = zf.read(kml_name).decode("utf-8")

    data = parse_kml(kml_text)

    all_features = (
        data["forecast_points"]
        + data["wind_radii"]
        + data["best_track_points"]
        + data["track_lines"]
    )

    geojson = {
        "type": "FeatureCollection",
        "features": all_features,
        "_meta": {
            "source":         "JTWC KMZ",
            "storm_name":     data["storm_name"],
            "kmz_file":       kmz_path.name,
            "forecast_points": len(data["forecast_points"]),
            "wind_radii":     len(data["wind_radii"]),
            "best_track_pts": len(data["best_track_points"]),
            "track_lines":    len(data["track_lines"]),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(geojson, ensure_ascii=False, indent=2))

    print(f"✓ {len(all_features)} features → {output_path}")
    print(f"  forecast points : {len(data['forecast_points'])}")
    print(f"  wind radii      : {len(data['wind_radii'])}")
    print(f"  best track pts  : {len(data['best_track_points'])}")
    print(f"  track lines     : {len(data['track_lines'])}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/kmz_to_geojson.py <input.kmz> [output.geojson]")
        sys.exit(1)

    kmz_path = Path(sys.argv[1])
    if not kmz_path.exists():
        print(f"Error: {kmz_path} not found")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        stem = kmz_path.stem.lower()
        output_path = REPO_ROOT / "data" / f"{stem}.geojson"

    convert(kmz_path, output_path)


if __name__ == "__main__":
    main()
