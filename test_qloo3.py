import json
from qloo_client import qloo_get, search_entity, get_insights

print("== TRAVEL ==")
for name in ["Hampi", "Goa", "Paris"]:
    hit = search_entity(name, "travel")
    print(name, "->", hit)
    if hit:
        try:
            for i in get_insights([hit[0]], "travel", take=3):
                print("  ", i["name"], i["match"], i["tags"])
        except Exception as e:
            print("   ERROR", e)

print("\n== FOOD TAGS ==")
for q in ["restaurant", "biryani", "indian"]:
    print("tags for", q)
    try:
        data = qloo_get("/v2/tags", {"filter.query": q, "take": 5})
        print(json.dumps(data)[:900])
    except Exception as e:
        print("   ERROR", e)