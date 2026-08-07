import json, urllib.request

r = urllib.request.urlopen('http://localhost:8000/api/wage-cards')
data = json.loads(r.read())
cards = [c for c in data.get('items', []) if c.get('site_codes', '').upper() == 'IXCE' and not c.get('is_pt')]

print(f"IXCE cards found: {len(cards)}")
print(f"{'BT':<12} {'Tenure':<7} {'MW':<10} {'Gross':<10} {'State':<6} {'City':<12}")
print("-" * 60)
for c in sorted(cards, key=lambda x: (x.get('short_bt', ''), x.get('tenure_years', 0))):
    print(f"{c.get('short_bt',''):<12} {c.get('tenure_years',0):<7} {c.get('minimum_wage',0):<10} {c.get('gross',0):<10} {c.get('state',''):<6} {c.get('city',''):<12}")
