# johanheilbron.nl

The source of the website **https://johanheilbron.nl**.
Every change saved here appears on the website by itself, usually within two minutes.

---

## The publication list

The list of publications on the website is taken from **your own Word file**:

`Documenten\Johan 1 - Werk\CV\- 1 PUBL78NU(NL).docx`

Keep working in that file exactly as you always have. It is the only source of the list;
nobody edits it except you. The website follows it whenever the list is synchronised (below).

## Adding PDFs

On your computer, the website lives in `Documenten\website`. Inside it is a folder **bib**
with one folder per section of your list:

| Folder | What goes in it |
|---|---|
| `bib\books` | Books, edited volumes, brochures |
| `bib\scientific-editions` | Scientific editions |
| `bib\articles-chapters` | Articles, book chapters, reviews, essays |
| `bib\journal-issues` | Thematic journal issues |
| `bib\film` | Filmography |

Copy PDFs into the right folder. **The file names do not matter.**
Try to keep each PDF under 20 MB.

## Putting the changes online ("sync")

After you have changed the Word list or added PDFs, the website needs to be synchronised.
Claude does this: open the Claude app, choose the **website** folder, and type:

> Sync the website.

Claude then reads your Word list, updates the publication list, finds out which publication
each new PDF belongs to, adds a **Download** button for it, and puts everything online.
It tells you what it changed. PDFs it could not identify with certainty are listed in
`bib\UNMATCHED.md`; it never guesses.

---

## About page and CV

These are ordinary text files that you can edit yourself:

- **About:** `content\about.md`
- **CV:** `content\cv.md`

Two ways to edit them:

1. **On github.com:** open the file, click the pencil icon (top right), change the text,
   click **Commit changes**.
2. **With Pages CMS:** go to https://app.pagescms.org, click **Sign in with GitHub**,
   choose the repository `johanheilbron.github.io`, and use the forms for
   *About page* and *CV*. Click **Save** when done.

Text between `*stars*` appears in italics. A line starting with `## ` is a heading.
In the CV, a line like `- 2008–2018: Professor ...` puts the years in the left column.

---

## Did it work?

Open the **Actions** tab at the top of the repository page on github.com. A green tick means
the website was updated. A red cross means something went wrong; the previous version of the
website stays online, so nothing breaks.
