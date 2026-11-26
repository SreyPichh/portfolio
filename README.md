# Portfolio: the home office

A hand-drawn home office you can click around in, plus About, Work, Notes and Contact pages.
It's a static site: plain HTML, CSS and JavaScript. A small Python script (no installs needed)
assembles the pages into `dist/`, and that folder is what goes online.

## Run it on your computer

```bash
python3 tools/build.py --serve
```

Open http://localhost:5173. Every time you save a file, the site rebuilds; refresh to see it.
Press Ctrl+C to stop.

## Where to change things

| What | Where |
| --- | --- |
| Name, monogram, role, city, email, résumé link, social links, site address | `site.json` |
| Page text (the `[bracketed]` placeholders) | `src/pages/*.html` |
| Page title and description | the `---` block at the top of each file in `src/pages/` |
| Projects (the postcards), the panels that open in the office, notes | `src/static/script.js`, near the top |
| Colours, spacing, fonts | `src/static/styles.css` |
| Top bar, shared drawings, page `<head>` | `src/partials/` (one copy, used by every page) |
| The office drawing itself | `tools/gen_room.py`, then `python3 tools/gen_room.py` (don't edit the room inside `src/pages/index.html` by hand) |
| Photos and files | `src/static/assets/` |

In pages and partials, `{{site.name}}` and similar are filled in from `site.json`, and
`{{> topbar}}` pastes in a file from `src/partials/`. If something is misspelled, the build
stops and tells you which file and which word.

## Before you publish

- [ ] Fill in `site.json`, including the real `url` the site will live at.
- [ ] Replace the `[bracketed]` placeholders. To list everything still left, with file and line:
      `python3 tools/build.py --check`
- [ ] Add a résumé: put the PDF in `src/static/assets/` and set `"resume": "assets/your-file.pdf"`.
- [ ] Give each project a real cover: add `cover: 'assets/your-image.jpg'` to it in `projects` in `script.js`.
- [ ] Check you have the right to use `src/static/assets/couple.png`.
- [ ] Decide whether to cover the certificate numbers on `src/static/assets/n4-certificate.jpg`.
- [ ] Remake the share picture once your name is in: run `python3 tools/make_images.py`
      while `--serve` is running (needs Google Chrome).
- [ ] Look at it in Safari, Firefox and on a real phone.

`inspo/` is never published: it's listed in `.gitignore`, and the build only uses `src/`.

## Put it online

Push this folder to a GitHub repository, then connect it to one of these (all have free plans):

- **Netlify**: "Add new site → Import an existing project". `netlify.toml` already sets the
  build command and folder, so just click Deploy.
- **Cloudflare Pages**: build command `python3 tools/build.py`, output directory `dist`.
- **Vercel**: framework "Other", build command `python3 tools/build.py`, output directory `dist`.

After the first deploy, each push to `main` publishes the new version. Add your own domain in the
host's settings, then put that address in `site.json` as `url`.

No GitHub? Run `python3 tools/build.py` and drag the `dist/` folder onto
https://app.netlify.com/drop.

**GitHub Pages** also works but needs a workflow that runs the build. If the site will live at
`username.github.io/repo-name/`, set `"basePath": "/repo-name/"` in `site.json` so the
"page not found" page can find its styles.

## What's in the folder

```
site.json          your details
src/pages/         one file per page (index, about, work, notes, contact, 404)
src/partials/      layout, top bar, shared drawings, project dialog
src/static/        styles.css, script.js, assets/, icons, share image (copied as-is)
tools/build.py     builds dist/ (and --serve for local work)
tools/gen_room.py  draws the office
tools/make_images.py  makes the phone icon and share picture
netlify.toml       deploy settings
dist/              the built site (made by the build, not saved in git)
```
