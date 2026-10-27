from qloo_client import search_entity, find_tag, get_insights

print("FOOD (biryani, Goa)")
t = find_tag("Biryani")
print("tag:", t)
try:
    for i in get_insights([], "food", take=4, city="Goa", tag_ids=[t]):
        print("  ", i["name"], i["match"], i["tags"])
except Exception as e:
    print("  ERROR", e)

print("TRAVEL (Goa)")
hit = search_entity("Goa", "travel")
for i in get_insights([hit[0]], "travel", take=3):
    print("  ", i["name"], i["match"], i["tags"])