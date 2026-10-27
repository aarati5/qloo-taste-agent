from qloo_client import qloo_get, search_entity, get_insights

for q in ["Radiohead", "Her", "Biryani", "Hampi"]:
    data = qloo_get("/search", {"query": q})
    print("SEARCH", q)
    for e in data.get("results", [])[:3]:
        print("  ", e.get("name"), e.get("types"))

tests = [("music", "Radiohead", ""), ("movies", "Her", ""),
         ("food", "Biryani", "Goa"), ("travel", "Hampi", "")]
for cat, name, city in tests:
    hit = search_entity(name)
    print("\n==", cat, name, hit)
    try:
        for i in get_insights([hit[0]], cat, take=3, city=city):
            print("  ", i)
    except Exception as e:
        print("   ERROR", e)