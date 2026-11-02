# johanheilbron.nl

The source of the website **https://johanheilbron.nl**.

Every change saved here appears on the website by itself, usually within two minutes.
No programming is needed for everyday updates.

---

## Adding a publication: the easy way (Pages CMS)

Pages CMS is a free website that gives you simple forms for editing this site.

1. Go to **https://app.pagescms.org** and click **Sign in with GitHub**.
   (The first time, GitHub asks whether Pages CMS may access your repositories: allow it
   for the repository `johanheilbron.github.io`.)
2. Choose the repository **johanheilbron.github.io**.
3. In the menu on the left, click **Publications**, then **Add an entry**.
4. Fill in the form:
   - **Title**, **Authors**, **Year**
   - **Section on the Research page**: Books, Edited volumes, Journal articles, Book chapters or Other writings
   - **Journal / publisher / book**: for example `Revue française de sociologie 55(3)` or `Paris: Seuil`
   - **PDF of the paper**: click it and upload the PDF from your computer (optional)
   - **Web link**: a DOI or publisher page (optional)
   - **Book cover image**: for books, a picture of the cover (optional)
5. Click **Save**. The website updates within a couple of minutes.

To correct or remove an entry: open it in **Publications**, change it and **Save**,
or tick **Hide from the website**. The About page and the CV can be edited the same way.

---

## Adding a publication directly on GitHub (no extra website needed)

**Step 1: upload the PDF**

1. On this page, open the folder **files**.
2. Click **Add file** (top right) → **Upload files**.
3. Drag the PDF into the window. Use a simple file name without spaces,
   for example `2026-sociology-of-translation.pdf`.
4. Click the green **Commit changes** button.

**Step 2: add the entry**

1. Go back to the main page of the repository, open **content**, then **publications**.
2. Click **Add file** → **Create new file**.
3. As the name, type for example `2026-sociology-of-translation.md`.
4. Copy the block below into the large text field and fill it in.
   Keep the quotation marks; remove a line if it does not apply.

```
---
title: "Title of the publication"
authors: "Johan Heilbron"
year: 2026
type: articles
venue: "Name of the journal or publisher"
pdf: files/2026-sociology-of-translation.pdf
link: https://doi.org/...
---
```

   For **type**, use one of: `books`, `edited`, `articles`, `chapters`, `other`.

5. Click **Commit changes**.

---

## Did it work?

Open the **Actions** tab at the top of this page. A green tick means the website was updated.
A red cross means something went wrong; the previous version of the website stays online,
so nothing breaks. The most common cause is a missing quotation mark in the block above.

---

## Where things are

| What | Where |
|---|---|
| Publications (one file each) | `content/publications/` |
| About page text | `content/about.md` |
| CV | `content/cv.md` |
| Research page introduction | `content/research.md` |
| Name, e-mail, Research page sections | `content/site.yaml` |
| PDFs | `files/` |
| Photo and book covers | `images/`, `images/covers/` |

Design and code (`templates/`, `assets/`, `build.py`) do not need to be touched for updates.
