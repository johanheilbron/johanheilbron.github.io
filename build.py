#!/usr/bin/env python3
"""
build.py: static site generator for johanheilbron.nl

Reads the content in content/ (Markdown and YAML), renders it through the
Jinja templates in templates/, and writes the finished site to _site/.
GitHub Actions runs this on every push.

The publication list comes from content/publications/<section>.yaml, which
an agent maintains from Johan's gold index (see CLAUDE.md). PDFs live in
bib/<section>/ and are published as they are.

Usage:
    uv run build.py          build the site into _site/
    uv run build.py serve    build, then preview at http://localhost:8000
"""

import hashlib
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
OUT = ROOT / "_site"

# Folders copied verbatim into the site
STATIC_DIRS = ["assets", "files", "images", "bib"]

# PDF size checks (GitHub Pages allows 1 GB for the whole site)
PDF_WARN_MB = 20
BIB_WARN_MB = 700

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


def local_path(value, default_dir):
    """Repo-relative path for a file reference ("x.pdf", "bib/books/x.pdf", "/bib/...")."""
    rel = str(value).strip().lstrip("/")
    return rel if "/" in rel else f"{default_dir}/{rel}"


def asset_url(value, default_dir, context):
    """Turn a file reference into a site URL.

    Accepts a full URL, a repo path ("bib/books/x.pdf" or "/bib/books/x.pdf"),
    or a bare file name (looked up in default_dir). Returns None, with a
    warning, if the file does not exist, so the site never shows a broken
    download link.
    """
    if not value:
        return None
    value = str(value).strip()
    if re.match(r"https?://", value):
        return value
    rel = local_path(value, default_dir)
    if not (ROOT / rel).is_file():
        warn(f"{context}: file '{value}' not found, link left out")
        return None
    return "/" + quote(rel)


def link_label(url):
    if "doi.org" in url:
        return "DOI"
    return "Publisher"


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
# Publications
# ---------------------------------------------------------------------------

def load_publications(sections_config):
    """Load content/publications/<id>.yaml for every section in site.yaml."""
    seen_ids = set()
    linked_pdfs = set()
    sections = []
    for sec in sections_config:
        sid = sec["id"]
        path = CONTENT / "publications" / f"{sid}.yaml"
        name = f"content/publications/{sid}.yaml"
        if not path.is_file():
            warn(f"{name} missing, section '{sec['label']}' left out")
            continue
        try:
            entries = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or []
        except yaml.YAMLError as e:
            warn(f"{name} could not be read ({e.__class__.__name__}), section left out")
            continue

        items = []
        for e in entries:
            if not isinstance(e, dict) or not e.get("title"):
                warn(f"{name}: entry without title skipped")
                continue
            if e.get("hidden"):
                continue
            eid = str(e.get("id", ""))
            if not eid or eid in seen_ids:
                warn(f"{name}: missing or duplicate id '{eid}'")
            seen_ids.add(eid)
            ctx = f"{name} [{eid}]"
            pdf = asset_url(e.get("pdf"), f"bib/{sid}", ctx)
            if pdf and pdf.startswith("/"):
                linked_pdfs.add((ROOT / local_path(e["pdf"], f"bib/{sid}")).resolve())
            link = str(e["link"]).strip() if e.get("link") else None
            try:
                year = int(e.get("year") or 0)
            except (TypeError, ValueError):
                warn(f"{ctx}: year '{e.get('year')}' is not a number")
                year = 0
            items.append({
                "id": eid,
                "year": year,
                "title": md_inline(str(e["title"])),
                "authors": md_inline(str(e.get("authors") or "")),
                "details": md_inline(str(e.get("details") or "")),
                "also": [md_inline(str(a)) for a in (e.get("also") or [])],
                "pdf": pdf,
                "fulltext": str(e["fulltext"]).strip() if e.get("fulltext") else None,
                "link": link,
                "link_label": e.get("link_label") or (link_label(link) if link else None),
                "cover": asset_url(e.get("cover"), "images/covers", ctx),
            })
        # Newest first; entries of the same year keep the order of the gold index
        items.sort(key=lambda p: -p["year"])
        if items:
            sections.append({**sec, "items": items})
    return sections, linked_pdfs


def check_bib(linked_pdfs):
    """Report PDFs in bib/ that no entry links to yet, and size problems."""
    bib = ROOT / "bib"
    if not bib.is_dir():
        return
    pdfs = sorted(p for p in bib.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf")
    total = 0
    unlinked = []
    for p in pdfs:
        size = p.stat().st_size
        total += size
        rel = p.relative_to(ROOT).as_posix()
        if size > PDF_WARN_MB * 1024 * 1024:
            warn(f"{rel} is {size / 1048576:.0f} MB; consider compressing it (limit for upload on github.com is 25 MB)")
        if p.resolve() not in linked_pdfs:
            unlinked.append(rel)
    if total > BIB_WARN_MB * 1024 * 1024:
        warn(f"bib/ holds {total / 1048576:.0f} MB of PDFs; GitHub Pages allows 1 GB for the whole site")
    print(f"  bib/: {len(pdfs)} PDF(s), {total / 1048576:.1f} MB, {len(unlinked)} not yet linked to the index")
    for rel in unlinked:
        print(f"    not linked: {rel}")


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
                            ignore=shutil.ignore_patterns(".gitkeep", "README*", "*.md"))

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

    pubs_meta, pubs_body = read_frontmatter(CONTENT / "publications.md")
    sections, linked_pdfs = load_publications(site["publication_sections"])
    render("publications.html", "publications/index.html", page="publications",
           intro=md(pubs_body), sections=sections, title=pubs_meta.get("title", "Publications"))

    cv_meta, cv_body = read_frontmatter(CONTENT / "cv.md")
    cv_pdf = asset_url(cv_meta.get("pdf"), "files", "content/cv.md")
    render("cv.html", "cv/index.html", page="cv", body=cv_html(cv_body), cv_pdf=cv_pdf)

    _, contact_body = read_frontmatter(CONTENT / "contact.md")
    render("contact.html", "contact/index.html", page="contact", body=md(contact_body))

    render("404.html", "404.html", page="404")

    if site.get("domain"):
        (OUT / "CNAME").write_text(site["domain"] + "\n", encoding="utf-8")

    check_bib(linked_pdfs)
    count = sum(len(s["items"]) for s in sections)
    print(f"Build complete: {count} publications, {len(warnings)} warning(s).")


def load_site():
    with open(CONTENT / "site.yaml", encoding="utf-8-sig") as f:
        return yaml.safe_load(f) or {}


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
