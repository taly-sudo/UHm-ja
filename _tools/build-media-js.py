#!/usr/bin/env python3
"""Rebuild media.js by scanning the media/ folder.

Run from anywhere:  python3 _tools/build-media-js.py
Any file you drop into media/<collection>/ is picked up automatically.
"""
import json, os, re, sys
from urllib.parse import quote

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA = os.path.join(SITE, "media")
OUT = os.path.join(SITE, "media.js")

IMG = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
VID = {".mp4", ".webm", ".mov", ".m4v"}

# Collection display names and blurbs. Unknown folders get a generic line.
META = {
 "vice-city-pack": ("Vice City Pack", "Vintage Vice City pack — the largest screenshot set in the folder."),
 "vice-city-style": ("Vice City Style", "Vice City style screenshots."),
 "classic-car-collection": ("Classic Car Collection", "Screenshots of the classic car collection."),
 "67-vapid-dominator-buggy": ("’67 Vapid Dominator Buggy", "Screenshots of the ’67 Vapid Dominator Buggy."),
 "95-grotti-cheetah": ("’95 Grotti Cheetah", "Screenshots of the ’95 Grotti Cheetah."),
 "ganado-retro-build": ("Ganado Retro Build", "Screenshot of the Ganado retro build."),
 "shitzu-squalo": ("Shitzu Squalo", "Screenshots of the Shitzu Squalo boat."),
 "jasons-safehouse-vehicles": ("Jason’s Safehouse Vehicles", "Screenshots of the vehicles at Jason’s safehouse."),
 "rideout-customs-mod-shop": ("Rideout Customs Mod Shop", "Screenshots from the Rideout Customs mod shop."),
 "one-eyed-willies-mod-shop": ("One-Eyed Willie’s Mod Shop", "Screenshots from One-Eyed Willie’s mod shop."),
 "electric-fang-tattoo-parlor": ("Electric Fang Tattoo Parlor", "Screenshots from the Electric Fang tattoo parlor."),
 "saras-unisex-salon": ("Sara’s Unisex Salon", "Screenshots from Sara’s unisex salon."),
 "stock-305-clothing-store": ("Stock 305 Clothing Store", "Screenshots from the Stock 305 clothing store."),
 "goodtime-gear": ("Goodtime Gear", "Screenshot from the Goodtime Gear store."),
 "ptt-youngins-illegal-goods-store": ("PTT Youngin$ Illegal Goods Store", "Screenshot from the PTT Youngin$ illegal goods store."),
 "hawk-and-little-morgan-revolvers": ("Hawk & Little Morgan Revolvers", "Screenshots of the Hawk & Little Morgan revolvers."),
 "personalized-weapon-variants": ("Personalized Weapon Variants", "Screenshot of personalized weapon variants."),
 "clips-discord": ("clips-discord", "Gameplay clips."),
}

# Collections listed first, in this order; the rest follow alphabetically.
FIRST = ["clips-discord"]


def pretty(name):
    base = os.path.splitext(name)[0]
    m = re.match(r"^(photo|video|clip)_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})", base, re.I)
    if m:
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        kind, y, mo, d, hh, mm = m.groups()
        word = "Photo" if kind.lower() == "photo" else "Clip"
        return "%s, %s %s %s at %s:%s" % (word, int(d), months[int(mo)-1], y, hh, mm)
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


def sortkey(slug):
    if slug in FIRST:
        return (0, FIRST.index(slug), "")
    return (1, 0, META.get(slug, (slug,))[0].lower().lstrip("’"))


if not os.path.isdir(MEDIA):
    sys.exit("no media/ folder next to %s" % OUT)

data = []
for slug in sorted(os.listdir(MEDIA), key=sortkey):
    folder = os.path.join(MEDIA, slug)
    if not os.path.isdir(folder):
        continue
    files = sorted(f for f in os.listdir(folder)
                   if os.path.splitext(f)[1].lower() in IMG | VID)
    if not files:
        continue
    name, desc = META.get(slug, (slug.replace("-", " ").title(),
                                 "Media from the “%s” folder." % slug))
    photos = sum(1 for f in files if os.path.splitext(f)[1].lower() in IMG)
    videos = len(files) - photos
    items, pi, vi = [], 0, 0
    for f in files:
        is_video = os.path.splitext(f)[1].lower() in VID
        if is_video:
            vi += 1
            label = "Clip %d of %d" % (vi, videos)
        else:
            pi += 1
            label = "Photo %d of %d" % (pi, photos)
        items.append({
            "path": "media/%s/%s" % (quote(slug), quote(f)),
            "type": "video" if is_video else "photo",
            "title": pretty(f),
            "label": label,
            "file": f,
            "mb": round(os.path.getsize(os.path.join(folder, f)) / 1048576, 1),
        })
    data.append({"name": name, "slug": slug, "desc": desc,
                 "photos": photos, "videos": videos, "items": items})

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("window.GALLERY = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")

print("collections: %d  photos: %d  videos: %d" % (
    len(data), sum(c["photos"] for c in data), sum(c["videos"] for c in data)))
