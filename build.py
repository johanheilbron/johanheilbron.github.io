#!/usr/bin/env python3
"""
build.py: static site generator for johanheilbron.nl

Reads the content in content/ (Markdown files with YAML front matter),
renders it through the Jinja templates in templates/, and writes the
finished site to _site/. GitHub Actions runs this on every push.

Usage:
    uv run build.py          build the site into _site/
    uv run build.py serve    build, then preview at http://localhost:8000
"""

import hashlib
import re
import shutil
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
OUT = ROOT / "_site"

# Folders copied verbatim into the site
STATIC_DIRS = ["assets", "files", "images"]

warnings = []


def warn(msg):
    warnings.append(msg)
    print(f"  WARNING: {msg}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_frontmatter(path):
    """Return (front matter dict, markdown body) for a Markdown file."""
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text.startswith("---"):
        return {}, text
    match = re.search(r"\n---[ \t]*(\n|$)", text[3:])
    if not match:
        return {}, text
    meta = yaml.safe_load(text[3:match.start() + 3]) or {}
    body = text[match.end() + 3:].strip()
    return meta, body


def md(text):
    """Markdown to HTML, with typographic quotes and dashes."""
    return markdown.markdown(text or "", extensions=["extra", "smarty", "sane_lists"])


def md_inline(text):
    """Markdown for a single line: no surrounding <p>."""
    html = md(text).strip()
    if html.startswith("<p>") and html.endswith("</p>") and html.count("<p>") == 1:
        html = html[3:-4]
    return html


def asset_url(value, default_dir, context):
    """Turn a file reference from front matter into a site URL.

    Accepts a full URL, a repo path ("files/x.pdf" or "/files/x.pdf"),
    or a bare filename (looked up in default_dir). Returns None, with a
    warning, if the file does not exist, so the site never shows a
    broken download link.
    """
    if not value:
        return None
    value = str(value).strip()
    if re.match(r"https?://", value):
        return value
    rel = value.lstrip("/")
    if "/" not in rel:
        rel = f"{default_dir}/{rel}"
    if not (ROOT / rel).is_file():
        warn(f"{context}: file '{value}' not found, link left out")
        return None
    return "/" + rel


def link_label(url):
    if "doi.org" in url:
        return "DOI"
    if "hal.science" in url or "archives-ouvertes" in url:
        return "HAL"
    return "Online"


YEAR_PREFIX = re.compile(
    r"^<li>((?:c\.\s*)?\d{4}(?:\s*[–—-]\s*(?:\d{4}|present|now|today|heden))?)\s*[:,]?\s*",
    re.IGNORECASE,
)


def cv_html(text):
    """Render the CV; list items that start with a year get a date column."""
    html = md(text)
    lines = []
    for line in html.split("\n"):
        m = YEAR_PREFIX.match(line)
        if m:
            line = f'<li class="dated"><span class="when">{m.group(1)}</span><span class="what">{line[m.end():]}'
            line = line.replace("</li>", "</span></li>")
        lines.append(line)
    html = "\n".join(lines)
    return html.replace("<ul>\n<li class=\"dated\">", "<ul class=\"dated\">\n<li class=\"dated\">")


# ---------------------------------------------------------------------------
# Content loaders
# ---------------------------------------------------------------------------

def load_site():
    with open(CONTENT / "site.yaml", encoding="utf-8-sig") as f:
        return yaml.safe_load(f) or {}


def load_publications(categories):
    known = {c["id"] for c in categories}
    pubs = []
    for path in sorted((CONTENT / "publications").glob("*.md")):
        name = f"content/publications/{path.name}"
        try:
            meta, body = read_frontmatter(path)
        except yaml.YAMLError as e:
            warn(f"{name}: could not read the top section ({e.__class__.__name__}), skipped")
            continue
        if not meta.get("title"):
            warn(f"{name}: no title, skipped")
            continue
        if meta.get("hidden"):
            continue
        kind = str(meta.get("type", "")).strip()
        if kind not in known:
            warn(f"{name}: unknown type '{kind}', shown under '{categories[-1]['label']}'")
            kind = categories[-1]["id"]
        link = str(meta["link"]).strip() if meta.get("link") else None
        fulltext = str(meta["fulltext"]).strip() if meta.get("fulltext") else None
        try:
            year = int(str(meta.get("year", "")).strip()[:4])
        except ValueError:
            year = None
        pubs.append({
            "title": md_inline(str(meta["title"])),
            "authors": md_inline(str(meta.get("authors", "") or "")),
            "venue": md_inline(str(meta.get("venue", "") or "")),
            "year": year,
            "year_label": meta.get("year", ""),
            "type": kind,
            "pdf": asset_url(meta.get("pdf"), "files", name),
            "cover": asset_url(meta.get("cover"), "images/covers", name),
            "link": link,
            "link_label": meta.get("link_label") or (link_label(link) if link else None),
            "fulltext": fulltext,
            "fulltext_label": meta.get("fulltext_label") or "Full text",
            "note": md_inline(body) if body else "",
        })
    # Newest first; undated items last
    pubs.sort(key=lambda p: (-(p["year"] or 0), p["title"].lower()))
    sections = []
    for cat in categories:
        items = [p for p in pubs if p["type"] == cat["id"]]
        if items:
            sections.append({**cat, "items": items})
    return sections


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build():
    site = load_site()
    # Empty _site/ rather than deleting it: on Windows a running preview
    # server or OneDrive can hold the folders open.
    OUT.mkdir(exist_ok=True)
    for child in OUT.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)
        else:
            child.unlink(missing_ok=True)

    for d in STATIC_DIRS:
        if (ROOT / d).is_dir():
            shutil.copytree(ROOT / d, OUT / d, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(".gitkeep", "README*"))

    css_hash = hashlib.md5((ROOT / "assets" / "style.css").read_bytes()).hexdigest()[:8]

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]))
    env.globals.update(site=site, css_version=css_hash)

    def render(template, out_path, **ctx):
        target = OUT / out_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(env.get_template(template).render(**ctx), encoding="utf-8")
        print(f"  wrote {out_path}")

    about_meta, about_body = read_frontmatter(CONTENT / "about.md")
    photo = asset_url(about_meta.get("photo"), "images", "content/about.md")
    render("about.html", "index.html", page="about", about=about_meta,
           photo=photo, body=md(about_body))

    research_meta, research_body = read_frontmatter(CONTENT / "research.md")
    sections = load_publications(site["research_categories"])
    render("research.html", "research/index.html", page="research",
           intro=md(research_body), sections=sections, title=research_meta.get("title", "Research"))

    cv_meta, cv_body = read_frontmatter(CONTENT / "cv.md")
    cv_pdf = asset_url(cv_meta.get("pdf"), "files", "content/cv.md")
    render("cv.html", "cv/index.html", page="cv", body=cv_html(cv_body), cv_pdf=cv_pdf)

    render("404.html", "404.html", page="404")

    if site.get("domain"):
        (OUT / "CNAME").write_text(site["domain"] + "\n", encoding="utf-8")

    count = sum(len(s["items"]) for s in sections)
    print(f"Build complete: {count} publications, {len(warnings)} warning(s).")


def serve(port=8000):
    import functools
    import http.server

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    print(f"Preview at http://localhost:{port}  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()


if __name__ == "__main__":
    build()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve()
