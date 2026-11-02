# CLAUDE.md: johanheilbron.nl

Personal academic website of Johan Heilbron (historical sociologist).
Repository: `johanheilbron/johanheilbron.github.io`, served at https://johanheilbron.nl
via GitHub Pages (custom domain registered at TransIP).

## Who uses this

- **Johan** (site owner) is not a programmer. He edits content through Pages CMS
  (`.pages.yml`) or the GitHub web interface; see README.md, which is written for him.
  Keep README.md accurate and in plain language whenever you change how content works.
- **Micha** (his son) set the site up and may ask agents for design changes.

## Architecture

- Plain static site, no Jekyll. `build.py` renders `content/` through Jinja templates
  in `templates/` into `_site/`.
- GitHub Actions (`.github/workflows/deploy.yml`) runs `uv run --frozen build.py` on every
  push to `main` and deploys `_site/` to Pages. `_site/` is never committed.
- Python environment is managed by **uv**: dependencies in `pyproject.toml` / `uv.lock`,
  local env in `.venv/` (gitignored). Never `pip install` globally; use `uv add <pkg>`.
- Three pages: About (`/`), Research (`/research/`), CV (`/cv/`). No news section: Johan
  is largely retired and explicitly does not want one.

## Content model

- `content/site.yaml`: name, e-mail, domain, and `research_categories` (order + labels of
  the Research page sections). If you change categories, update the `type` select options
  in `.pages.yml` and the list of types in README.md too.
- `content/publications/*.md`: one file per publication, named `YEAR-short-slug.md`.
  Front matter: `title` (required), `authors`, `year`, `type` (category id), `venue`,
  `pdf` (local file → "Download PDF" button), `fulltext` (free online version, e.g. HAL,
  Cairn, Persée), `link` (DOI or publisher page), `link_label`, `fulltext_label`, `cover`,
  `hidden`. Optional body = short note.
  Conventions: leave `authors` empty for sole-authored work (it is his own site); for
  co-authored work list everyone in order as initials + surname ("M. van Bottenburg &
  J. Heilbron"), with "(eds)" for edited volumes. Italicise journal and book titles in
  `venue` with Markdown (`*European Journal of Social Theory* 2(4): 429–444`).
  `year` may be a range such as "1997–2010"; sorting uses the first four digits.
  Within a section, entries sort newest first.
- `pdf`/`cover`/`photo` accept `files/x.pdf`, `/files/x.pdf` (Pages CMS style), a bare
  filename, or a full URL. Missing local files produce a build warning and the link is
  left out, so the site never shows broken downloads.
- `content/cv.md`: Markdown. List items that start with a year or year range
  (`- 2005–2020 Text`) are rendered with a date column.
- PDFs in `files/`, images in `images/` (covers in `images/covers/`).

## Commands (PowerShell on Windows; uv is on PATH)

- Build: `uv run build.py`
- Preview: `uv run build.py serve` → http://localhost:8000 (or the `site` entry in
  `.claude/launch.json`)
- Always build and check for `WARNING` lines before committing.

## Adding papers on Johan's behalf

1. Copy the PDF into `files/` with a short, space-free name (`YEAR-short-slug.pdf`).
2. Create `content/publications/YEAR-short-slug.md` with the front matter above.
   Quote strings containing colons.
3. `uv run build.py`, check the Research page in the preview.
4. Commit and push: `git add -A; git commit -m "Add <short title>"; git push`.
   Git authenticates over SSH with the key in `~/.ssh/id_ed25519` (account `johanheilbron`).
5. The Actions run deploys within ~2 minutes; check with `gh run list --limit 3`.

## Design principles

- Simple, quiet, typographic. A scholar's site, modelled on the Research tab Johan liked
  on Stephen Mennell's academia.edu page: centred name, tab navigation, and a Research
  page with a section index on the left and entries (optional cover, title, authors,
  Download button) on the right.
- Fonts: Newsreader (serif, text and titles), Source Sans 3 (labels, navigation, metadata).
- Colours: warm paper background, near-black ink, one restrained oxblood accent for links.
- No icons, badges, tags, gradients, cards or shadows. No frameworks; one CSS file
  (`assets/style.css`) with variables at the top, one tiny script (`assets/site.js`).
- Must work on phones: the Research index becomes a wrapped row above the list.
