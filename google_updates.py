import json
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict

import requests

PRODUCT_ID = "rGHU1u87FJnkP6W2GwMi"
INCIDENTS_URL = "https://status.search.google.com/incidents.json"
UPDATES_FILE = "updates.json"

def fetch_and_store_updates() -> List[Dict]:
    """Fetch incidents for the product and store them locally."""
    response = requests.get(INCIDENTS_URL, timeout=10)
    response.raise_for_status()
    incidents = response.json()
    product_incidents = [
        inc for inc in incidents
        if inc.get("service_key") == PRODUCT_ID
        or any(p.get("id") == PRODUCT_ID for p in inc.get("affected_products", []))
    ]
    with open(UPDATES_FILE, "w", encoding="utf-8") as f:
        json.dump(product_incidents, f, indent=2)
    return product_incidents

def get_recent_updates(days: int = 30) -> List[Dict]:
    """Return updates from the last ``days`` days.

    Updates are fetched from Google's Search Status Dashboard and cached
    locally in ``updates.json``.
    """
    try:
        data = fetch_and_store_updates()
    except Exception:
        if not os.path.exists(UPDATES_FILE):
            raise
        with open(UPDATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = []
    for inc in data:
        when = inc.get("most_recent_update", {}).get("when") or inc.get("begin")
        try:
            when_dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
        except Exception:
            continue
        if when_dt >= cutoff:
            recent.append(inc)
    return recent
