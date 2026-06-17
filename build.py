#!/usr/bin/env python3
"""Generate the indie-dev showcase site from live App Store data + the Mission Control brain."""
import os, json, urllib.request, html

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = "/Users/venetsiakrasteva/MissionControl/projects"
ICONS = os.path.join(HERE, "assets", "icons")
os.makedirs(ICONS, exist_ok=True)

# App Store ids in display order; (brain id for tagline/accent, appstore id, status)
APPS = [
    ("hammynest", "6760735030", "live"),
    ("symply",    "6771794811", "live"),
    ("neated",    "6764564726", "live"),
    ("loafe",     "6775538020", "live"),
    ("moshed",    "6761011260", "live"),
    ("evenfall",  "6780470703", "soon"),
]

def brain(pid):
    try:
        return json.load(open(os.path.join(BRAIN, f"{pid}.json")))
    except Exception:
        return {}

# Live App Store metadata (icons, canonical urls, genre)
ids = ",".join(a[1] for a in APPS)
store = {}
try:
    with urllib.request.urlopen(f"https://itunes.apple.com/lookup?id={ids}&country=gb", timeout=20) as r:
        for it in json.load(r).get("results", []):
            store[str(it["trackId"])] = it
except Exception as e:
    print("lookup failed:", e)

cards = []
for pid, aid, status in APPS:
    b = brain(pid)
    it = store.get(aid, {})
    name = b.get("name") or it.get("trackName") or pid
    tagline = b.get("tagline") or it.get("primaryGenreName") or ""
    accent = b.get("accent") or "#7B61FF"
    platforms = b.get("platforms") or ([] if "macOS" not in (it.get("primaryGenreName") or "") else ["macOS"])
    url = it.get("trackViewUrl") or (b.get("links", {}) or {}).get("appStore") or ""
    # download icon
    icon_rel = ""
    art = it.get("artworkUrl512") or it.get("artworkUrl100")
    if art:
        try:
            dst = os.path.join(ICONS, f"{aid}.png")
            urllib.request.urlretrieve(art, dst)
            icon_rel = f"assets/icons/{aid}.png"
        except Exception as e:
            print("icon fail", aid, e)
    plats = "".join(f'<span class="plat">{html.escape(p)}</span>' for p in platforms)
    icon_html = (f'<img class="icon" src="{icon_rel}" alt="{html.escape(name)} icon">'
                 if icon_rel else
                 f'<div class="icon placeholder" style="background:{accent}">{html.escape(name[:1])}</div>')
    if status == "soon":
        action = '<span class="badge soon">Coming soon</span>'
    elif url:
        action = f'<a class="badge store" href="{html.escape(url)}" target="_blank" rel="noopener">View on the App Store ↗</a>'
    else:
        action = ""
    cards.append(f"""
      <article class="card" style="--accent:{accent}">
        {icon_html}
        <h2>{html.escape(name)}</h2>
        <p class="tag">{html.escape(tagline)}</p>
        <div class="plats">{plats}</div>
        {action}
      </article>""")

page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Venetsia — indie apps for Apple platforms</title>
<meta name="description" content="Small, focused, privacy-respecting apps for iPhone, iPad, Mac & Apple Watch — by Venetsia, indie developer.">
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;
         background:radial-gradient(1200px 600px at 50% -10%, #1c1b2e, #0c0c11 60%); color:#ececf2; min-height:100vh; }}
  .wrap {{ max-width:1040px; margin:0 auto; padding:72px 24px 56px; }}
  header {{ text-align:center; margin-bottom:48px; }}
  header h1 {{ font-size:clamp(34px,6vw,56px); margin:0 0 10px; letter-spacing:-0.02em; }}
  header p {{ font-size:18px; color:#a8a8b8; max-width:560px; margin:0 auto; line-height:1.5; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }}
  .card {{ background:linear-gradient(180deg,#17171f,#121219); border:1px solid #24242f; border-radius:20px;
          padding:24px; display:flex; flex-direction:column; align-items:flex-start;
          box-shadow:0 1px 0 #ffffff0a inset, 0 0 0 0 var(--accent); transition:transform .15s, box-shadow .15s, border-color .15s; }}
  .card:hover {{ transform:translateY(-3px); border-color:var(--accent); box-shadow:0 14px 40px -18px var(--accent); }}
  .icon {{ width:84px; height:84px; border-radius:21%; margin-bottom:16px; object-fit:cover;
          box-shadow:0 6px 18px -8px #000; }}
  .icon.placeholder {{ display:flex; align-items:center; justify-content:center; font-size:38px; font-weight:700; color:#fff; }}
  .card h2 {{ font-size:21px; margin:0 0 6px; }}
  .tag {{ color:#a8a8b8; font-size:14px; line-height:1.5; margin:0 0 16px; flex:1; }}
  .plats {{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:18px; }}
  .plat {{ font-size:11px; font-weight:600; color:#c9c9d6; background:#ffffff12; padding:3px 9px; border-radius:999px; }}
  .badge {{ font-size:14px; font-weight:600; text-decoration:none; padding:9px 16px; border-radius:11px; }}
  .badge.store {{ background:var(--accent); color:#fff; }}
  .badge.store:hover {{ filter:brightness(1.08); }}
  .badge.soon {{ background:#ffffff14; color:#b9b9c8; }}
  footer {{ text-align:center; color:#6f6f80; font-size:13px; margin-top:56px; }}
  footer a {{ color:#9a9ad0; }}
</style></head>
<body><div class="wrap">
  <header>
    <h1>Venetsia</h1>
    <p>Indie developer. I build small, focused, privacy-respecting apps for iPhone, iPad, Mac &amp; Apple Watch.</p>
  </header>
  <main class="grid">{''.join(cards)}</main>
  <footer>Made solo, with care. · <a href="https://github.com/venetsia">GitHub</a></footer>
</div></body></html>"""

open(os.path.join(HERE, "index.html"), "w").write(page)
print(f"Built index.html with {len(cards)} apps; icons in assets/icons/")
