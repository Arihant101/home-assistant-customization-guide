"""Build index.html from README.md.

Usage: python3 build/build.py README.md build/template.html index.html
Tables preceded by <!-- gallery --> become card grids on the site.
"""
import html
import re
import sys

import markdown

src_path, tpl_path, out_path = sys.argv[1:4]
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

# Wrap each H2 section so it can be styled as a glass panel.
parts = re.split(r'(?=<h2 id=")', content)
content = parts[0] + "".join(f'<section class="panel">{p}</section>' for p in parts[1:])

def toc_item(t):
    name = t["name"]
    if name[:2].isdigit():
        num, label = name[:2], name[4:].strip()
    else:
        num, label = "★", name
    return f'<a href="#{t["id"]}"><span class="num">{num}</span>{label}</a>'


toc = "".join(toc_item(t) for t in toc_tokens)

tpl = open(tpl_path, encoding="utf-8").read()
out = (
    tpl.replace("{{TITLE}}", html.escape(title))
    .replace("{{INTRO}}", intro_html)
    .replace("{{TOC}}", toc)
    .replace("{{CONTENT}}", content)
)
open(out_path, "w", encoding="utf-8").write(out)
print(f"built {out_path}: {len(out)//1024} KB, {content.count('class=\"card\"')} cards, {len(toc_tokens)} sections")
