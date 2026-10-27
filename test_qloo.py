import json
import httpx
from qloo_client import BASE_URL, API_KEY, search_entity


def call(path, params):
    r = httpx.get(BASE_URL + path, params=params,
                  headers={"X-Api-Key": API_KEY}, timeout=20)
    print(r.status_code)
    try:
        print(json.dumps(r.json(), indent=2)[:1300])
    except Exception:
        print(r.text[:800])


hit = search_entity("Radiohead")
print("search_entity ->", hit)
rid = hit[0]

for t in ["urn:entity:artist", "urn:entity:movie",
          "urn:entity:place", "urn:entity:destination"]:
    print("=====", t)
    call("/v2/insights", {
        "filter.type": t,
        "signal.interests.entities": rid,
        "take": 3,
    })