# dasmachtdas.de – DAS GmbH

Statische Website (kein Framework), Hosting über Vercel.

- `public/` – fertige Website (wird von Vercel ausgeliefert, kein Build nötig)
- `_src/` – Quellen: `build.py` (Seiten, Schema, robots, sitemap, llms), `assets/css`, `assets/js`, `icons`
- `vercel.json` – Clean URLs, Security-Header, Caching

Änderungen: `_src/build.py` bzw. CSS/JS bearbeiten, dann `python3 _src/build.py` ausführen und `public/` committen.
