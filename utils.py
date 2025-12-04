# utils.py
import re
from dateutil import parser as dateparser
from datetime import datetime

def parse_duration_seconds(duration_str):
    """Parse ISO8601 duration like PT1H2M3S into seconds."""
    if not duration_str:
        return 0
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
    m = re.match(pattern, duration_str)
    if not m:
        return 0
    hours = int(m.group(1)) if m.group(1) else 0
    minutes = int(m.group(2)) if m.group(2) else 0
    seconds = int(m.group(3)) if m.group(3) else 0
    return hours*3600 + minutes*60 + seconds

def to_iso_start(date_str):
    dt = dateparser.parse(date_str)
    dt = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def to_iso_end(date_str):
    dt = dateparser.parse(date_str)
    dt = datetime(dt.year, dt.month, dt.day, 23, 59, 59)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
