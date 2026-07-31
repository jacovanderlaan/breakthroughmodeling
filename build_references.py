#!/usr/bin/env python3
"""Render W:/data/rules/mdde-references/references.yaml into <site>/references.html.
Simple YAML-ish parser (no pyyaml dependency). Source of truth = W:.

Usage: python build_references.py <site_dir> "<sitename>" '<brand-html>'
"""
import os, sys, re, html

SRC = "W:/data/rules/mdde-references/references.yaml"

def parse(path):
    """Minimal parser for our known structure: intro, groups[].{name,note,books[].{title,author,borrow,url}}."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    data = {"intro": "", "groups": []}
    i = 0
    # intro (folded >)
    while i < len(lines):
        if lines[i].startswith("intro:"):
            i += 1
            buf = []
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].strip() == ""):
                if lines[i].strip() == "" and buf: break
                buf.append(lines[i].strip())
                i += 1
            data["intro"] = " ".join(x for x in buf if x)
            break
        i += 1
    # groups
    text = "\n".join(lines)
    gblocks = re.split(r"\n  - name:", text)
    for gb in gblocks[1:]:
        name = re.match(r"\s*(.+)", gb).group(1).strip()
        note_m = re.search(r"\n\s*note:\s*(.+)", gb)
        note = note_m.group(1).strip() if note_m else ""
        books = []
        for bb in re.split(r"\n\s*- title:", gb)[1:]:
            title = re.match(r"\s*(.+)", bb).group(1).strip()
            au = re.search(r"\n\s*author:\s*(.+)", bb)
            bo = re.search(r"\n\s*borrow:\s*(.+)", bb)
            ur = re.search(r"\n\s*url:\s*(.+)", bb)
            books.append({"title": title,
                          "author": au.group(1).strip() if au else "",
                          "borrow": bo.group(1).strip() if bo else "",
                          "url": ur.group(1).strip() if ur else ""})
        data["groups"].append({"name": name, "note": note, "books": books})
    return data

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="robots" content="noindex, nofollow" /><!-- TESTPHASE-NOINDEX: remove at go-live -->
<title>References — {sitename}</title>
<meta name="description" content="The books, authors and bodies of work Breakthrough Modeling draws on." />
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml" />
<link rel="stylesheet" href="assets/site.css" />
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html">{brand}</a>
    <nav class="main">
      <a href="index.html">Home</a>
      <a href="concepts/index.html">Concepts</a>
      <a href="references.html">References</a>
      <a class="cta" href="https://structurebeatsmagic.com">The method &rarr;</a>
    </nav>
  </div>
</header>
<div class="hero wrap" style="padding-bottom:20px">
  <div class="eyebrow">Standing on the shoulders of giants</div>
  <h1>References</h1>
  <p class="sub">{intro}</p>
</div>
<section class="wrap">
{groups}
  <p style="margin-top:34px"><a href="index.html">&larr; Back home</a></p>
</section>
<footer><div class="wrap">
  <p><span class="badge">Test phase</span> &nbsp; Part of the <a href="https://structurebeatsmagic.com">Structure Beats Magic</a> family.</p>
</div></footer>
</body>
</html>
"""

def esc(s): return html.escape(s or "")

def build(site_dir, sitename, brand):
    d = parse(SRC)
    groups_html = ""
    for g in d["groups"]:
        cards = ""
        for b in g["books"]:
            t = f'<a href="{esc(b["url"])}">{esc(b["title"])}</a>' if b["url"] else esc(b["title"])
            cards += (f'<div class="ref-book"><div class="ref-t">{t}</div>'
                      f'<div class="ref-a">{esc(b["author"])}</div>'
                      f'<div class="ref-b">{esc(b["borrow"])}</div></div>\n')
        note = f'<p class="muted">{esc(g["note"])}</p>' if g["note"] else ""
        groups_html += f'<h2>{esc(g["name"])}</h2>\n{note}\n<div class="ref-grid">\n{cards}</div>\n'
    out = os.path.join(site_dir, "references.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(PAGE.format(sitename=sitename, brand=brand, intro=esc(d["intro"]), groups=groups_html))
    n = sum(len(g["books"]) for g in d["groups"])
    print(f"  built references.html: {len(d['groups'])} groups, {n} books -> {out}")

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "Breakthrough Modeling",
          sys.argv[3] if len(sys.argv) > 3 else 'Breakthrough Modeling <span class="abbr">BTM</span>')
