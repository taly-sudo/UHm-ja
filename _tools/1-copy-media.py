import os, re, shutil, json, unicodedata
SRC = os.path.expanduser("~/mnt/gtra6")
OUT = os.path.join(SRC, "website", "media")

def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("’","").replace("'","").replace("&","and").replace("$","s")
    s = re.sub(r"[^A-Za-z0-9._-]+","-", s)
    s = re.sub(r"-+","-", s).strip("-.").lower()
    return s or "item"

IMG = {".jpg",".jpeg",".png",".webp",".gif"}
VID = {".mp4",".webm",".mov",".m4v"}

os.makedirs(OUT, exist_ok=True)
manifest = []
for entry in sorted(os.listdir(SRC)):
    if entry == "website": continue
    p = os.path.join(SRC, entry)
    if os.path.isdir(p):
        coll = entry
        cslug = slug(entry)
        dst = os.path.join(OUT, cslug)
        os.makedirs(dst, exist_ok=True)
        for f in sorted(os.listdir(p)):
            ext = os.path.splitext(f)[1].lower()
            if ext not in IMG | VID: continue
            fs = slug(f)
            target = os.path.join(dst, fs)
            if not os.path.exists(target) or os.path.getsize(target) != os.path.getsize(os.path.join(p,f)):
                shutil.copy2(os.path.join(p,f), target)
            manifest.append({"collection": coll, "cslug": cslug, "src": f,
                             "path": f"media/{cslug}/{fs}",
                             "type": "video" if ext in VID else "photo",
                             "bytes": os.path.getsize(target)})
    else:
        continue  # loose root-level files are intentionally excluded
        ext = os.path.splitext(entry)[1].lower()
        if ext not in IMG | VID: continue
        cslug = "unsorted"
        dst = os.path.join(OUT, cslug); os.makedirs(dst, exist_ok=True)
        fs = slug(entry)
        target = os.path.join(dst, fs)
        if not os.path.exists(target) or os.path.getsize(target) != os.path.getsize(p):
            shutil.copy2(p, target)
        manifest.append({"collection": "Loose Files", "cslug": cslug, "src": entry,
                         "path": f"media/{cslug}/{fs}",
                         "type": "video" if ext in VID else "photo",
                         "bytes": os.path.getsize(target)})

json.dump(manifest, open("/tmp/manifest.json","w"), indent=1, ensure_ascii=False)
print(len(manifest), "items;", sum(m['bytes'] for m in manifest)//1048576, "MB")
