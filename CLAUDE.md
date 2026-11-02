# CLAUDE.md: johanheilbron.nl

Personal academic website of Johan Heilbron (historical sociologist, largely retired).
Repository: `johanheilbron/johanheilbron.github.io`, served at https://johanheilbron.nl
via GitHub Pages (custom domain registered at TransIP).

## Who uses this

- **Johan** (site owner) is not a programmer. He maintains his publication list and CV in
  Word, drops PDFs into `bib/`, and asks Claude to "sync the website". README.md is written
  for him; keep it accurate and in plain language whenever you change how things work.
- **Micha** (his son) set the site up and may ask agents for design changes.

## RULE ZERO: the gold files are read-only

Two of Johan's Word files are the **gold sources** of the site:

    C:\Users\johan\OneDrive\Documenten\Johan 1 - Werk\CV\- 1 PUBL78NU(NL).docx                        (publications: "the gold index")
    C:\Users\johan\OneDrive\Documenten\Johan 1 - Werk\CV\- 2 Heilbron CV (English complete) <year>.docx (CV)

- **Never edit, move, rename, copy over, re-save or "fix" these files, or anything else in
  `Johan 1 - Werk`.** Not even typos. Only Johan changes them. If you think something in
  them is wrong, tell him.
- Read them **only** through `uv run tools/read_index.py` (publications) and
  `uv run tools/read_index.py --cv` (CV, newest year in the file name). These open the files
  read-only and write text snapshots into this repo, with e-mail addresses removed.
  `.claude/settings.json` denies Claude's edit tools on that folder; do not weaken that rule,
  and do not write there from scripts or shell commands.
- Snapshots and content are public. Never put an e-mail address in plain text into the repo.

## Architecture

- Plain static site, no Jekyll. `build.py` renders `content/` through Jinja templates in
  `templates/` into `_site/`. GitHub Actions (`.github/workflows/deploy.yml`) runs
  `uv run --frozen build.py` on every push to `main` and deploys `_site/` (never committed).
- Python environment managed by **uv** (`pyproject.toml`, `uv.lock`, local `.venv/`).
  Never `pip install` globally; use `uv add <pkg>`.
- Pages: About (`/`, `content/about.md`), Publications (`/publications/`), CV (`/cv/`,
  `content/cv.md`), Contact (`/contact/`, `content/contact.md`). No news section, by request.
- E-mail (anti-spam): `content/site.yaml` holds only `email_encoded` (address reversed, then
  base64; make it with `uv run tools/encode_email.py name@example.org`). The Contact page
  shows a plain "Send an e-mail" link; `assets/site.js` decodes the address on click and
  opens a mailto: link. The address itself is never displayed. Current address: his
  planet.nl address (see the encoded value).

## CV data

- `content/cv.md` mirrors the CV part of the Word CV (everything before its "Publications"
  heading), section by section, as Markdown lists. Same fidelity rules as the publications:
  no paraphrasing or correcting; only make table cells that ran together readable
  ("Secondary schoolLyceum" → "Secondary school: Lyceum"), drop stray invisible characters,
  and wrap URLs in `<...>` so they are clickable. Never copy the address/e-mail header block.
  The CV's own publication list is ignored; the Publications page comes from the gold index.
- `content/cv-snapshot.txt`: text snapshot of the Word CV at the last sync.

## Publication data

- `content/site.yaml` → `publication_sections`: the sections of the Publications page, in
  order, mirroring the sections of the gold index:

  | Section id | Gold index section |
  |---|---|
  | `books` | Books / Ouvrages / Boeken / Brochures |
  | `scientific-editions` | Scientific editions |
  | `articles-chapters` | Articles, chapters, scientific book reviews |
  | `journal-issues` | Thematic journal issues |
  | `film` | Filmography |

- `content/publications/<section-id>.yaml`: one YAML list per section. Generated and
  maintained by agents from the gold index; never edited by Johan. Schema per entry:

  ```yaml
  - id: "2015-french-sociology"   # stable: "<year>-<first words of title>", unique site-wide; never change an existing id
    year: 2015                     # integer; for articles, the year heading it sits under in the index
    authors: "Julien Duval, Johan Heilbron (dir.)"   # as written before the title; omit if Johan is sole author or none is written
    title: "French Sociology"      # without surrounding quotation marks; *italic* allowed
    details: "Ithaca/London: Cornell University Press, 2015."   # rest of the reference, as written, minus URLs
    also:                          # optional: translations, reprints, continuation lines that belong to this entry
      - "*La Sociologie française...*, Paris : CNRS Éditions, 2020."
    fulltext: "https://..."        # optional: openly readable full text (Persée, HAL /document, OpenEdition, AST archive, ...)
    link: "https://doi.org/..."    # optional: DOI or publisher page
    pdf: "any file name.pdf"       # optional: a file in bib/<section-id>/ (or a path starting with bib/)
    cover: "file.jpg"              # optional: image in images/covers/
    hidden: true                   # optional: keep in the data but not on the site
  ```

  Text is **faithful to the index**: no paraphrasing, translating or correcting (typos stay).
  Only split into fields, strip the quotes around the title, and move URLs into
  `fulltext`/`link`. Entries are listed in index order; the build sorts each section by
  `year`, newest first, keeping index order within a year.
- `content/publications/index-snapshot.txt`: text snapshot of the gold index at the last
  sync (one paragraph per line, `*...*` = italic). `git diff` on it shows what Johan changed.
- `bib/<section-id>/`: Johan's PDFs, any file name, unstructured. Published as-is under
  `/bib/...`. Never rename or move his files. A PDF shows on the site only once an entry's
  `pdf:` points to it; the build lists PDFs that are not linked yet.

## The sync routine ("sync the website")

Run these steps in order and report to Johan in plain language what changed.

1. **Snapshot the index.** `uv run tools/read_index.py`, then `git diff content/publications/index-snapshot.txt`.
2. **Update the data** for every changed, added or removed paragraph:
   - added → new entry in the right section file, in index order, following the schema;
   - changed → update that entry's fields, keep its `id`, `pdf` and `cover`;
   - removed → delete the entry; if it had a `pdf`, leave the file in `bib/` and mention it.
   Use the section headings and year headings in the snapshot to place entries.
3. **Link new PDFs.** `uv run build.py` lists "not linked" PDFs. For each: read it (the
   Read tool reads PDFs; the first pages usually suffice), identify the publication, and set
   `pdf:` on that entry (file name only if it is in the entry's own section folder). A PDF in
   the "wrong" folder is fine: link it with its full `bib/...` path.
   If you are not sure, do not guess: add it to `bib/UNMATCHED.md` (file, what you found,
   candidate entries) and tell Johan. Remove resolved items from that file.
4. **Sync the CV.** `uv run tools/read_index.py --cv`, then `git diff content/cv-snapshot.txt`.
   Apply changes in the CV part (before "Publications") to `content/cv.md`, following
   "CV data" above. Changes in the CV's own publication list need no action.
5. **Build and check.** `uv run build.py` must end without new `WARNING` lines. Preview with
   `uv run build.py serve` (http://localhost:8000/publications/) if you changed anything visible.
6. **Commit and push.** `git add -A; git commit -m "Sync: <short summary>"; git push`.
   Git authenticates over SSH (`~/.ssh/id_ed25519`, account `johanheilbron`). The Actions run
   deploys within ~2 minutes; check with `gh run list --limit 3`.

## Other commands (PowerShell on Windows)

- If `uv`, `git` or `gh` are not found, refresh PATH first:
  `$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')`
- Build: `uv run build.py` · Preview: `uv run build.py serve` → http://localhost:8000
- Size limits: GitHub Pages allows 1 GB for the whole site and github.com uploads up to 25 MB
  per file. The build warns for PDFs over 20 MB and for `bib/` over 700 MB; compress large
  scans, or host them on HAL or Zenodo and put the URL in `fulltext`.

## Design principles

- Minimal, pre-AI-era academic. Structure from the Research tab Johan liked on Stephen
  Mennell's academia.edu page (centred name, navigation, section index on the left, entries
  on the right). Micha pointed to s-m.ac as an example of restraint, NOT as a style to copy;
  do not imitate it (no Tufte/ET Book look).
- **Avoid "AI default" styling.** Micha explicitly rejected it. That means: no hairline rules or
  dividers, no underlined-tab bars, no letter-spaced uppercase labels, no sans-serif UI text,
  no "tasteful" accent colours (terracotta, oxblood), no cream/"paper" backgrounds,
  no buttons/boxes/cards, no icons, badges, gradients or shadows.
- One typeface: Libre Caslon Text (Google Fonts), regular, italic and bold. Plain upright
  headings. Ink #1d1d1d on white; secondary text #6b6b6b; links a plain muted blue (#2a4b8d),
  underlined. Navigation is grey with the current page in black.
- Spacing does the separating, not lines. No frameworks; one CSS file, one tiny script.
- Must work on phones: the section index becomes a wrapped row above the list.
