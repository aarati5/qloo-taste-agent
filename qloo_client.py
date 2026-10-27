import os

import httpx
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://hackathon.api.qloo.com"
API_KEY = os.getenv("QLOO_API_KEY", "")

# Category -> Qloo entity type
TYPE_MAP = {
    "music": "urn:entity:artist",
    "movies": "urn:entity:movie",
    "food": "urn:entity:place",
    "travel": "urn:entity:destination",
}


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


def _items(data):
    """Find the list of results, whichever shape Qloo returns."""
    if not isinstance(data, dict):
        return []
    r = data.get("results", data)
    if isinstance(r, dict):
        r = r.get("entities") or r.get("results") or []
    return r if isinstance(r, list) else []


def search_entity(name: str, category=None):
    """Name -> (entity_id, official_name), or None.
    If a category is given, picks the first result of the matching Qloo type."""
    want = TYPE_MAP.get(category) if category else None
    items = _items(qloo_get("/search", {"query": name}))
    if want:
        items = [e for e in items if want in (e.get("types") or [])]
    if not items:
        return None
    e = items[0]
    return (e.get("entity_id") or e.get("id"), e.get("name"))


def find_tag(name: str):
    """Food word (e.g. Biryani) -> best Qloo tag id, or None."""
    data = qloo_get("/v2/tags", {"filter.query": name, "take": 10})
    tags = (data.get("results") or {}).get("tags") or []
    for prefix in ("urn:tag:cuisine", "urn:tag:specialty_dish",
                   "urn:tag:genre:place:restaurant"):
        for t in tags:
            if (t.get("id") or "").startswith(prefix):
                return t["id"]
    return tags[0]["id"] if tags else None


def get_insights(entity_ids, category, take=5, city="", tag_ids=None):
    """Taste-matched results from Qloo for one category."""
    params = {"filter.type": TYPE_MAP[category], "take": take}
    if entity_ids:
        params["signal.interests.entities"] = ",".join(entity_ids)
    if tag_ids:
        params["signal.interests.tags"] = ",".join(tag_ids)
    if category == "food":
        params["filter.tags"] = "urn:tag:genre:place:restaurant"
        if city:
            params["filter.location.query"] = city

    attempts = [dict(params)]
    if "filter.location.query" in params:
        p = dict(params)
        p.pop("filter.location.query")
        attempts.append(p)

    data, last = None, None
    for p in attempts:
        try:
            data = qloo_get("/v2/insights", p)
            break
        except httpx.HTTPStatusError as e:
            last = e
    if data is None:
        raise last

    out = []
    for e in _items(data):
        props = e.get("properties") or {}
        aff = (e.get("query") or {}).get("affinity")
        out.append({
            "name": e.get("name"),
            "match": round(aff * 100) if isinstance(aff, (int, float)) else None,
            "tags": [t.get("name") for t in (e.get("tags") or [])[:4] if t.get("name")],
            "about": props.get("short_description") or "",
        })
    return out