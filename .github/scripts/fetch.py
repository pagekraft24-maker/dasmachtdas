import json, os, re, urllib.request, urllib.parse, ssl
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Referer": "https://dasmachtdas.de/"}
ctx = ssl.create_default_context()
def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        return r.status, r.headers.get("Content-Type", ""), r.read(), r.geturl()
out = "partner-raw"; os.makedirs(out, exist_ok=True); log = []
for p in json.load(open(".github/scripts/partners.json")):
    slug = re.sub(r"[^a-z0-9]+", "-", p["name"].lower()).strip("-")
    d = os.path.join(out, slug); os.makedirs(d, exist_ok=True)
    def save(url, name):
        try:
            st, ct, b, _ = get(url)
            if st == 200 and ("image" in ct or url.split("?")[0].endswith((".svg", ".png", ".webp", ".jpg"))) and len(b) > 200:
                ext = "svg" if "svg" in ct else ("png" if "png" in ct else ("webp" if "webp" in ct else ("jpg" if "jpeg" in ct else "bin")))
                open(os.path.join(d, f"{name}.{ext}"), "wb").write(b); log.append(f"OK {slug} {name} {len(b)} {url[:120]}")
            else: log.append(f"NO {slug} {name} {st} {ct} {url[:120]}")
        except Exception as e: log.append(f"ERR {slug} {name} {e} {url[:120]}")
    save(p["orig"], "orig")
    if p["site"]:
        try:
            st, ct, b, final = get(p["site"])
            h = b.decode("utf-8", "ignore")
            open(os.path.join(d, "page.html"), "w").write(h)
            cands = []
            for m in re.finditer(r'<img[^>]+>', h, re.I):
                tag = m.group(0)
                if re.search(r'logo', tag, re.I):
                    src = re.search(r'(?:data-src|src)=["\']([^"\']+)', tag)
                    if src: cands.append(src.group(1))
            for m in re.finditer(r'<meta[^>]+property=["\']og:image["\'][^>]*content=["\']([^"\']+)', h, re.I): cands.append(m.group(1))
            for m in re.finditer(r'<link[^>]+rel=["\'][^"\']*(?:apple-touch-icon|icon)[^"\']*["\'][^>]*href=["\']([^"\']+)', h, re.I): cands.append(m.group(1))
            seen = []
            for c in cands:
                u = urllib.parse.urljoin(final, c.replace("&amp;", "&"))
                if u not in seen and not u.startswith("data:"): seen.append(u)
            for i, u in enumerate(seen[:6]): save(u, f"c{i}")
        except Exception as e: log.append(f"ERR {slug} page {e}")
open(os.path.join(out, "log.txt"), "w").write("\n".join(log))
print("\n".join(log))
