import json, os, re, html

SITE = os.path.expanduser("~/mnt/gtra6/website")
manifest = json.load(open("/tmp/manifest.json"))

DESC = {
 "Vice City Pack": "Vintage Vice City pack — the largest screenshot set in the folder.",
 "Vice City Style": "Vice City style screenshots.",
 "Classic Car Collection": "Screenshots of the classic car collection.",
 "’67 Vapid Dominator Buggy": "Screenshots of the ’67 Vapid Dominator Buggy.",
 "’95 Grotti Cheetah": "Screenshots of the ’95 Grotti Cheetah.",
 "Ganado Retro Build": "Screenshot of the Ganado retro build.",
 "Shitzu Squalo": "Screenshots of the Shitzu Squalo boat.",
 "Jason’s Safehouse Vehicles": "Screenshots of the vehicles at Jason’s safehouse.",
 "Rideout Customs Mod Shop": "Screenshots from the Rideout Customs mod shop.",
 "One-Eyed Willie’s Mod Shop": "Screenshots from One-Eyed Willie’s mod shop.",
 "Electric Fang Tattoo Parlor": "Screenshots from the Electric Fang tattoo parlor.",
 "Sara’s Unisex Salon": "Screenshots from Sara’s unisex salon.",
 "Stock 305 Clothing Store": "Screenshots from the Stock 305 clothing store.",
 "Goodtime Gear": "Screenshot from the Goodtime Gear store.",
 "PTT Youngin$ Illegal Goods Store": "Screenshot from the PTT Youngin$ illegal goods store.",
 "Hawk & Little Morgan Revolvers": "Screenshots of the Hawk & Little Morgan revolvers.",
 "Personalized Weapon Variants": "Screenshot of personalized weapon variants.",
 "clips-discord": "Gameplay clips saved from Discord.",
 "Loose Files": "Videos and photos that sat loose in the folder, not in any collection.",
}

ORDER = ["clips-discord"]
SKIP = {"Loose Files"}
colls = {}
for m in manifest:
    if m["collection"] in SKIP: continue
    colls.setdefault(m["collection"], []).append(m)

def sortkey(name):
    if name in ORDER: return (0, ORDER.index(name), "")
    return (1, 0, name.lower().lstrip("’"))

def pretty(src):
    base = os.path.splitext(src)[0]
    m = re.match(r"^photo_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})", base)
    if m:
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        y, mo, d, hh, mm = m.groups()
        return "Photo, %s %s %s at %s:%s" % (int(d), months[int(mo)-1], y, hh, mm)
    base = re.sub(r"^\[.*?\]\s*", "", base)
    base = re.sub(r"^redvid[ _]io[ _]", "", base, flags=re.I)
    base = re.sub(r"^Screenshots?\s+", "", base)
    base = base.replace("_", " ")
    if " " not in base and base.count("-") >= 2:
        base = base.replace("-", " ")
    base = re.sub(r"\s+", " ", base).strip()
    if re.fullmatch(r"[a-z0-9]{5,8}", base):
        return "Untitled clip (%s)" % base
    base = re.sub(r"(?<=[A-Za-z])(\d+)$", r" \1", base)
    base = re.sub(r"\bgta\b", "GTA", base, flags=re.I)
    base = re.sub(r"\bio\b", "", base)
    base = re.sub(r"\s+", " ", base).strip()
    return base[:1].upper() + base[1:]

data = []
for name in sorted(colls, key=sortkey):
    items = colls[name]
    photos = sum(1 for i in items if i["type"] == "photo")
    videos = len(items) - photos
    entries = []
    pi = vi = 0
    for it in items:
        if it["type"] == "photo":
            pi += 1; label = "Photo %d of %d" % (pi, photos)
        else:
            vi += 1; label = "Clip %d of %d" % (vi, videos)
        entries.append({
            "path": it["path"], "type": it["type"],
            "title": pretty(it["src"]),
            "label": label,
            "file": it["src"],
            "mb": round(it["bytes"] / 1048576, 1),
        })
    data.append({
        "name": name, "slug": items[0]["cslug"],
        "desc": DESC.get(name, "Media from the “%s” folder." % name),
        "photos": photos, "videos": videos, "items": entries,
    })

os.makedirs(SITE, exist_ok=True)
with open(os.path.join(SITE, "media.js"), "w", encoding="utf-8") as f:
    f.write("window.GALLERY = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")
print("collections:", len(data), "items:", sum(len(c["items"]) for c in data))
