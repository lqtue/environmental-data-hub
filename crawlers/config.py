"""
config.py — Shared constants for all Environmental Data Hub crawlers.

Edit this file to add/remove stations, lakes, or provinces.
"""

# ── Lake Water (Thuy Loi Vietnam) ────────────────────────────────────────────

LAKE_API_BASE = (
    "http://e15.thuyloivietnam.vn/CanhBaoSoLieu/ATCBDTHo"
    "?lakename=&lakeref=9CBE33CD-5CFB-4CB9-BAEB-59147A825DF0"
    "%2Cc9a8c4ca-f1bb-467f-82c4-0999294af8fc"
    "%2C73bb8be6-bbd6-4042-8360-30abdced336a"
    "%2C0CE5BB74-C0BB-4C3F-8F2F-2F99485098AD"
    "%2CFCAEF9CF-E464-41E0-BA6D-9F973FD70931"
    "%2CE8174520-E0E0-41E0-BA6D-9F973FD70931"
    "%2C929f34bb-4d88-4364-8882-4099e75bcfd5"
    "%2C7D5B7DB0-D64A-4A36-BD4E-54A95CA62E9D"
    "%2CD0C28BB9-FE47-4BC2-B0DB-445038C1D1C5"
    "%2CDBEBBF2B-EB44-4996-A896-AE93E8257DC4"
    "%2C062A7CF0-46F3-4E99-8BCD-040CEF304344"
    "%2C9BFF6E76-94E2-4233-B659-258D74A1C95F"
    "%2C8DDDF139-D18F-484B-8BE8-832EF79861F6"
    "%2C4AB3F3C8-D7F4-44AA-8P9C-E93BDCFA1DCC"
    "&basinref=&provinceref=&capcongtrinh=&ishothuydien=0"
    "&nghidinh=&cocuavan=&congtacquanly=&sfrom=&sto="
    "&dtfrom=&dtto=&ccfrom=&ccto=&cdfrom=&cdto="
    "&quytrinhvanhanh=&hoxungyeu="
    "&time=2025-10-31+00%3A00%3A00%2C000"
)

# LakeCode → display position (Left, Top) and canvas name
LAKE_POSITION_MAP = {
    "0CE5BB74-C0BB-4C3F-8F2F-2F99485098AD": {"pos": "2269,560",  "canvas": "SongSrepok"},
    "4AB3F3C8-D7F4-44AA-897C-E93BDCFA1DCC": {"pos": "3791,677",  "canvas": "SongBa"},
    "73bb8be6-bbd6-4042-8360-30abdced336a": {"pos": "2327,2389", "canvas": "SongBa"},
    "7D5B7DB0-D64A-4A36-BD4E-54A95CA62E9D": {"pos": "1974,2889", "canvas": "SongBa"},
    "8DDDF139-D18F-484B-8BE8-832EF79861F6": {"pos": "1601,1918", "canvas": "SongSrepok"},
    "929f34bb-4d88-4364-8882-4099e75bcfd5": {"pos": "3149,892",  "canvas": "SongTraKhuc"},
    "9BFF6E76-94E2-4233-B659-258D74A1295F": {"pos": "1548,1170", "canvas": "SongKon"},
    "9CBE33CD-5CFB-4CB9-BAEB-59147A825DF0": {"pos": "2077,876",  "canvas": "SongBa"},
    "D0C28BB9-FE47-4BC2-B0DB-445038C1D1C5": {"pos": "1460,3256", "canvas": "SongBa"},
    "c9a8c4ca-f1bb-467f-82c4-0999294af8fc": {"pos": "1709,1640", "canvas": "SongKon"},
    "062A7CF0-46F3-4E99-8BCD-040CEF304344": {"pos": "2900,2066", "canvas": "SongKon"},
}

LAKE_FIELDS = [
    "Date", "LakeName", "LakeCode", "BasinName", "ProvinceName",
    "TdMucNuoc (Mực nước - m)", "TdDungTich (Dung tích - m3)",
    "TkDungTich (Dung tích thiết kế - m3)",
    "TiLeDungTichTdSoTk (Tỷ lệ dung tích - %)",
    "QDen (m3/s)", "QXa (m3/s)", "ThoiGianCapNhat (GMT+7)",
    "X", "Y", "Left", "Top", "CanvasName",
]

# ── Landslide / Flash Flood (NCHMF) ──────────────────────────────────────────

LANDSLIDE_ENDPOINT = (
    "https://luquetsatlo.nchmf.gov.vn/LayerMapBox/getDSCanhbaoSLLQ"
)
LANDSLIDE_SOGIO_DU_BAO = 6  # fixed per API spec

# Provinces to filter (exact match against provinceName_2cap field)
LANDSLIDE_TARGET_PROVINCES = {
    "TP. Huế", "TP. Đà Nẵng", "Quảng Ngãi", "Gia Lai", "Đắk Lắk",
}

LANDSLIDE_SEVERITY_RANK = {
    "Rất cao": 3,
    "Cao":    2,
    "Trung bình": 1,
}

# ── River Water Levels (VNDMS) ────────────────────────────────────────────────

RIVER_LIST_URL   = "https://vndms.dmptc.gov.vn/water_level"
RIVER_DETAIL_URL = "https://vndms.dmc.gov.vn/home/detailRain"
RIVER_ALERT_LEVELS = ["0", "1", "2", "3"]
RIVER_TIME_SELECT = "7"   # days of history to fetch
RIVER_DELAY = 0.25        # seconds between API calls (be polite)

# Station IDs to include (fetching all ~1000+ is slow; keep to monitored set)
ALLOWED_STATION_IDS = {
    "69716", "69718", "71540", "71549",
    "71558", "71559", "71708", "71709",
}

RIVER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (newsroom emergency fetch; Python)",
    "Accept":     "application/json, text/javascript, */*; q=0.9",
    "Referer":    "https://vndms.dmptc.gov.vn/",
}
