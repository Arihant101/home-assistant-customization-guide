"""Build the multi-page site from README.md.

Usage: python3 build/build.py README.md build/template.html .
Each H2 section of the README lands on one of the pages in PAGES.
Tables preceded by <!-- gallery --> become card grids, and the table after
<!-- devices --> becomes the sortable device guide.
"""
import html
import re
import sys

import markdown

src_path, tpl_path, out_dir = sys.argv[1:4]
src = open(src_path, encoding="utf-8").read()
title_line, body = src.split("\n", 1)
title = title_line.lstrip("# ").strip()

# Pull the intro paragraph (first non-empty line after the H1) into the hero.
intro, body = body.lstrip().split("\n", 1)

md = markdown.Markdown(
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
    extension_configs={"toc": {"toc_depth": "2-2", "anchorlink": False}},
)
content = md.convert(body)
toc_tokens = md.toc_tokens
intro_html = markdown.markdown(intro)

# file, nav label, icon, one-line description, section numbers ("SRC" = Sources)
PAGES = [
    ("index.html", "Home", "🏠", "Start here: the 60-minute glow-up.", ["00"]),
    ("setup.html", "Setup & security", "🐳", "What changed in 2026, Docker Desktop limits and fixes, remote access and hardening.", ["01", "02", "03"]),
    ("connect.html", "Marketplace & integrations", "🔌", "Must-install Marketplace projects, plus every integration for your devices and homelab.", ["04", "05"]),
    ("dashboards.html", "Dashboards & cards", "🧩", "Dashboard frameworks and a big gallery of custom cards.", ["06", "07"]),
    ("themes.html", "Themes", "🎨", "Ready-made themes and the DIY Aero Glass theme.", ["08"]),
    ("showcase.html", "Showcase & configs", "🏆", "Famous dashboards from Reddit and GitHub, and configs worth studying.", ["09", "10"]),
    ("devices.html", "Device shopping guide", "🛒", "43 devices you can sort by price, setup, popularity and how common they are.", ["19"]),
    ("automations.html", "Automations & workshops", "🍳", "Automation recipes, the 36-idea cookbook, blueprints, workshops and events.", ["11", "20"]),
    ("voice-ai.html", "Voice, AI & cameras", "🤖", "A local voice assistant on your Ollama, AI extras and Frigate cameras.", ["12", "13"]),
    ("cyber.html", "Cyber corner", "🛡️", "Home Assistant as an attack surface and as a security monitoring tool.", ["14"]),
    ("diy.html", "DIY & wall panels", "🛠️", "ESPHome builds, niche hardware, kiosks and wall panels.", ["15", "16"]),
    ("resources.html", "Free swaps & resources", "📚", "Paid → free alternatives, where to keep learning, and sources.", ["17", "18", "SRC"]),
]


def sec_key(sid):
    return sid[:2] if sid[:2].isdigit() else "SRC"


PAGE_OF = {num: pg[0] for pg in PAGES for num in pg[4]}
SEC_ID = {sec_key(t["id"]): t["id"] for t in toc_tokens}
missing = [k for k in SEC_ID if k not in PAGE_OF]
assert not missing, f"sections not assigned to a page: {missing}"

# Turn "§11" references into links to the page that holds that section.
content = re.sub(
    r"§(\d{2})",
    lambda m: f'<a class="sref" href="{PAGE_OF[m.group(1)]}#{SEC_ID[m.group(1)]}">§{m.group(1)}</a>'
    if m.group(1) in SEC_ID else m.group(0),
    content,
)

GH = re.compile(r'href="https://github\.com/([\w.-]+/[\w.-]+)"')


def cell_text(s):
    return re.sub(r"<[^>]+>", " ", s)


def card(cells, last_label):
    shot, name, desc, get = (cells + ["", "", "", ""])[:4]
    img = re.search(r'<img[^>]*src="([^"]+)"', shot)
    letter = html.escape(cell_text(name).strip()[:1].upper() or "•")
    if img:
        fig = (
            f'<figure class="shot"><img src="{img.group(1)}" alt="" loading="lazy" '
            f'decoding="async" referrerpolicy="no-referrer" '
            f"onerror=\"this.parentElement.classList.add('noimg')\">"
            f'<span class="orb">{letter}</span></figure>'
        )
    else:
        fig = f'<figure class="shot noimg"><span class="orb">{letter}</span></figure>'
    m = GH.search(name)
    stars = ""
    if m:
        repo = m.group(1)
        stars = (
            f'<img class="stars" alt="GitHub stars" loading="lazy" '
            f'src="https://img.shields.io/github/stars/{repo}?style=flat-square&amp;label=%E2%98%85&amp;color=0a84ff" '
            f"onerror=\"this.remove()\">"
        )
    search = html.escape(" ".join(cell_text(x) for x in (name, desc, get)).lower(), quote=True)
    return (
        f'<article class="card" data-search="{search}">{fig}'
        f'<div class="body"><h4>{name}</h4><p>{desc}</p>'
        f'<div class="meta"><span class="pill" title="{html.escape(last_label)}">{get}</span>{stars}</div></div></article>'
    )


def gallery(m):
    table = m.group(1)
    head = re.findall(r"<th[^>]*>(.*?)</th>", table, re.S)
    last_label = cell_text(head[-1]).strip() if head else ""
    rows = re.findall(r"<tr>(.*?)</tr>", table.split("</thead>", 1)[-1], re.S)
    cards = [card(re.findall(r"<td[^>]*>(.*?)</td>", r, re.S), last_label) for r in rows]
    return '<div class="gallery">' + "".join(cards) + "</div>"


content = re.sub(r"<!-- gallery -->\s*<table>(.*?)</table>", gallery, content, flags=re.S)


def num(text, default=0):
    """Midpoint of a price like '$40–60' (or the single number in '$49')."""
    vals = [int(v) for v in re.findall(r"\d+", text.replace(",", ""))]
    return round(sum(vals) / len(vals)) if vals else default


def device_card(cells, idx):
    name, cat, price, setup, pop, common, via, fit, why = (cells + [""] * 9)[:9]
    cat_txt = html.unescape(cell_text(cat)).strip()
    icon, _, cat_name = cat_txt.partition(" ")
    setup_lvl = 1 if "🟢" in setup else 2 if "🟡" in setup else 3
    fit_lvl = 2 if "✅" in fit else 1 if "⚠️" in fit else 0
    search = html.escape(" ".join(cell_text(x) for x in (name, cat, via, fit, why)).lower(), quote=True)
    return (
        f'<article class="card dev" data-idx="{idx}" data-search="{search}" data-cat="{html.escape(cat_name)}" '
        f'data-price="{num(cell_text(price))}" data-setup="{setup_lvl}" data-pop="{pop.count("★")}" '
        f'data-common="{common.count("●")}" data-fit="{fit_lvl}">'
        f'<div class="dev-top"><span class="dev-ico">{icon}</span><span class="dev-price">{price}</span></div>'
        f'<div class="body"><h4>{name}</h4><p>{why}</p>'
        f'<div class="dev-meta"><span class="tag s{setup_lvl}" title="Setup difficulty">{setup}</span>'
        f'<span class="tag" title="Popularity: how often the community recommends it">{pop}</span>'
        f'<span class="tag" title="How common it is in HA homes">{common}</span></div>'
        f'<div class="via"><b>Works via:</b> {via}</div><div class="fit f{fit_lvl}">{fit}</div></div></article>'
    )


def devices(m):
    table = m.group(1)
    rows = re.findall(r"<tr>(.*?)</tr>", table.split("</thead>", 1)[-1], re.S)
    cells = [re.findall(r"<td[^>]*>(.*?)</td>", r, re.S) for r in rows]
    cats = []
    for c in cells:
        t = html.unescape(cell_text(c[1])).strip()
        if t not in cats:
            cats.append(t)
    cat_btns = '<button type="button" class="chipbtn on" data-cat="all">All</button>' + "".join(
        f'<button type="button" class="chipbtn" data-cat="{html.escape(t.partition(" ")[2])}">{html.escape(t)}</button>' for t in cats
    )
    tools = (
        '<div class="devtools">'
        '<label class="sortlbl">Sort by <select id="devsort">'
        '<option value="idx">Recommended order</option>'
        '<option value="price-asc">Price: low → high</option>'
        '<option value="price-desc">Price: high → low</option>'
        '<option value="setup-asc">Setup: easiest first</option>'
        '<option value="setup-desc">Setup: hardest first</option>'
        '<option value="pop-desc">Popularity: most → least</option>'
        '<option value="common-desc">Most common → least common</option>'
        '<option value="common-asc">Least common → most common (niche picks)</option>'
        '</select></label>'
        '<label class="toggle"><input type="checkbox" id="devfit"> Only what works on my Docker Desktop setup</label>'
        '<span id="devcount"></span>'
        f'<div class="chiprow" id="devcats">{cat_btns}</div></div>'
    )
    return tools + '<div class="gallery devgrid" id="devgrid">' + "".join(device_card(c, i) for i, c in enumerate(cells)) + "</div>"


content = re.sub(r"<!-- devices -->\s*<table>(.*?)</table>", devices, content, flags=re.S)
content = content.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
content = re.sub(r"<p>🎯", '<p class="tldr">🎯', content)
content = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', content)
content = content.replace("<li>[ ] ", '<li class="todo"><input type="checkbox"> ')

# Split into H2 sections; each one becomes a glass panel on its page.
parts = re.split(r'(?=<h2 id=")', content)
preamble = parts[0].replace("<hr />", "").strip()
sections = {}
for part in parts[1:]:
    sid = re.match(r'<h2 id="([^"]+)"', part).group(1)
    sections[sec_key(sid)] = (sid, f'<section class="panel">{part.replace("<hr />", "")}</section>')
names = {t["id"]: t["name"] for t in toc_tokens}


def sub_label(sid):
    name = names[sid]
    if name[:2].isdigit():
        return name[:2], name[4:].strip()
    return "★", name


def nav(current):
    out = []
    for f, label, icon, _desc, nums in PAGES:
        on = f == current
        out.append(f'<a class="pg{" on" if on else ""}" href="{f}"><span class="pi">{icon}</span>{html.escape(label)}</a>')
        if on and len(nums) > 1:
            subs = "".join(
                f'<a href="#{sections[n][0]}"><span class="num">{sub_label(sections[n][0])[0]}</span>{sub_label(sections[n][0])[1]}</a>'
                for n in nums
            )
            out.append(f'<div class="subs" id="toc">{subs}</div>')
    return "".join(out)


def page_cards():
    return '<div class="pagegrid">' + "".join(
        f'<a class="pagecard" href="{f}"><span class="pi">{icon}</span><b>{html.escape(label)}</b><small>{html.escape(desc)}</small></a>'
        for f, label, icon, desc, _ in PAGES[1:]
    ) + "</div>"


SEARCH = (
    '<div class="search"><input id="q" type="search" placeholder="Filter this page… (try “glass”, “energy”, “reddit”)" '
    'aria-label="Filter cards on this page"><span id="count"></span></div>'
)
CHIPS = (
    '<div class="chips"><span class="chip">🏠 HA 2026.11</span><span class="chip">🐳 Docker Desktop · Windows 11</span>'
    '<span class="chip">🆓 Free &amp; open source</span><span class="chip">🖼️ 100+ projects</span><span class="chip">🛒 43 devices</span>'
    '<span class="chip">🍳 36 automations</span></div>'
)

tpl = open(tpl_path, encoding="utf-8").read()
total_cards = 0
for i, (f, label, icon, desc, nums) in enumerate(PAGES):
    body_html = "".join(sections[n][1] for n in nums)
    has_cards = 'class="card' in body_html
    if i == 0:
        header = (
            f'<header class="hero glass"><h1>{html.escape(title)}</h1><div class="intro">{intro_html}</div>{CHIPS}'
            f'<h3 class="pg-h">Pick a page</h3>{page_cards()}</header>'
        )
        body_html = (f'<div class="preamble">{preamble}</div>' if preamble else "") + body_html
        page_title = title
    else:
        header = (
            f'<header class="hero glass small"><div class="crumbs"><a href="index.html">Home</a> › {html.escape(label)}</div>'
            f'<h1><span class="hi">{icon}</span>{html.escape(label)}</h1><p class="lede">{html.escape(desc)}</p>'
            f'{SEARCH if has_cards else ""}</header>'
        )
        page_title = f"{label} · {title}"
    prev_pg = PAGES[i - 1] if i > 0 else None
    next_pg = PAGES[i + 1] if i + 1 < len(PAGES) else None
    pager = '<nav class="pager" aria-label="Pages">' + (
        f'<a class="gloss" href="{prev_pg[0]}">← {prev_pg[2]} {html.escape(prev_pg[1])}</a>' if prev_pg else "<span></span>"
    ) + (
        f'<a class="gloss green" href="{next_pg[0]}">{next_pg[2]} {html.escape(next_pg[1])} →</a>' if next_pg else "<span></span>"
    ) + "</nav>"
    out = (
        tpl.replace("{{PAGE_TITLE}}", html.escape(page_title))
        .replace("{{HEADER}}", header)
        .replace("{{NAV}}", nav(f))
        .replace("{{CONTENT}}", body_html)
        .replace("{{PAGER}}", pager)
    )
    open(f"{out_dir}/{f}", "w", encoding="utf-8").write(out)
    total_cards += body_html.count('class="card')
    print(f"  {f:18} {len(out)//1024:4} KB  sections {','.join(nums)}")
print(f"built {len(PAGES)} pages, {total_cards} cards, {len(sections)} sections")
