import os
import httpx
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://hackathon.api.qloo.com"
API_KEY = os.getenv("QLOO_API_KEY", "")


def qloo_get(path: str, params: dict) -> dict:
    """Calls Qloo. Returns {} if no key yet (demo mode)."""
    if not API_KEY:
        return {}
    r = httpx.get(
        BASE_URL + path,
        params=params,
        headers={"X-Api-Key": API_KEY},
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

    
 # Category -> Qloo entity type. Confirm these in docs: "Supported Entity Types".
TYPE_MAP = {
    "music": "urn:entity:artist",
    "movies": "urn:entity:movie",
    "food": "urn:entity:place",
    "travel": "urn:entity:destination",
}


def _items(data):
    """Find the list of results, whichever shape Qloo returns."""
    if not isinstance(data, dict):
        return []
    r = data.get("results", data)
    if isinstance(r, dict):
        r = r.get("entities") or r.get("results") or []
    return r if isinstance(r, list) else []


def search_entity(name: str):
    """Name -> (entity_id, official_name), or None."""
    items = _items(qloo_get("/search", {"query": name}))
    if not items:
        return None
    e = items[0]
    return (e.get("entity_id") or e.get("id"), e.get("name"))


def get_insights(entity_ids: list, category: str, take: int = 5):
    """Taste-matched results from Qloo for one category."""
    params = {
        "filter.type": TYPE_MAP[category],
        "signal.interests.entities": ",".join(entity_ids),
        "take": take,
    }
    out = []
    for e in _items(qloo_get("/v2/insights", params)):
        props = e.get("properties") or {}
        out.append({
            "name": e.get("name"),
            "about": props.get("short_description") or e.get("subtype") or "",
        })
    return out