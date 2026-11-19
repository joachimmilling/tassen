# Tassen

Find, compare and prioritize kindergartens (barnehager) in Oslo, Bærum, Asker, Lillestrøm, Lørenskog and Nordre Follo.

**Live:** https://joachimmilling.github.io/tassen/

The app itself is in Norwegian. It is one static page, `index.html`, which loads map tiles, fonts and kindergarten texts from `map/` when they are needed. MapLibre GL JS is loaded from jsDelivr.

Map tiles in `map/u/` are small files so only what is on screen loads: `l9_*` (one zoom 9 tile each), `l10_*` and `l11_*`
(four tiles each), `a<x>_<y>` (one zoom 12 tile, and outside the towns also its zoom 13 and 14 tiles) and `b<x>_<y>`
(one zoom 13 tile with its four zoom 14 tiles). `TKEYS` in `index.html` lists the files that exist.

For search engines, every kindergarten also has a small static page in `b/<slug>/` and every district one in `d/<slug>/`. They hold the key facts and link into the app (`#<slug>` opens that kindergarten). `sitemap.xml` lists all pages, and `og.png` is the image shown when a link is shared.

## Daily vacancy updates

`.github/workflows/update-vacancies.yml` runs twice a day. It downloads the open-places data collected by
[ledige-barnehageplasser-oslo](https://github.com/torkilv/ledige-barnehageplasser-oslo) and runs
`scripts/update_vacancies.py`, which writes `data/vacancies.json` (read by the app), the list on
`r/ledige-barnehageplasser-oslo/` and the RSS feed `vacancies.xml`. `data/kindergartens.json` is the index it
matches names against. `deadlines.ics` holds the application deadline with reminders.

## For AI assistants

`llms.txt` describes the site for AI assistants, including a link format that opens the app with a parent's setup
already filled in (`#home=…&work=…&born=…&prio=…`; read by `applySetup` in `index.html` and cleared from the address
bar once read). `data/kindergarten-facts.json` has the key facts per kindergarten with English field names.

## English version

`en/` holds the English pages. `en/index.html` is the same app with a small translator that rewrites the Norwegian
interface as it renders; text written by the kindergartens and municipalities stays in Norwegian.

## Municipalities

Oslo (by district), Bærum, Asker, Lillestrøm, Lørenskog and Nordre Follo. Every kindergarten is compared with the others in
its Oslo district or municipality. In the four municipalities added last, the description, food text and phone come
from the kindergarten's page at the municipality where it has one (mostly the municipal kindergartens). Without one,
food shows as not stated (with an estimate from the food fee) and visit mode asks about it. Plots, outdoor area and
nearby nature are measured the same way as in Oslo and Bærum. Nine kindergartens without a position in Barnehagefakta
are placed at their address point from Kartverket's address register. The home's municipality comes from the municipal borders, which decides the address rules in "Sjansen for plass".
The parent survey trend goes back to 2018 for every kindergarten (overall satisfaction, 1 to 5, the same scale every year).

The transit network is the earlier Oslo and Bærum network plus the lines and line patterns that reach the new
municipalities (night and school buses left out). Neighbouring stops are found on a grid, so setting it up takes a few
milliseconds even with about 2,400 stops.

## Questions per kindergarten and visit mode

`unknowns()` in `index.html` lists what is unclear about one kindergarten from its own data: facts that are missing or
only estimated, parent survey scores clearly below the district average, admission rules, and the age group it takes.
"Spør barnehagen" turns the most important ones into an email draft, and visit mode (`#besok-<slug>`) shows them on the
day of the visit with room for answers, things to look for, stars and notes. All of it stays in the browser
(`localStorage`, key `bhl-visits`). Once a visit is rated, the stars count for half of that kindergarten's score, and
the stars and words (not the notes or answers) travel in the shared list link (`#liste-<id>r<stars>t<words>`).

## Offline, share cards and bike routes

- `sw.js` (service worker) and `manifest.webmanifest`: the app can be added to the home screen and opens without a
  connection. Pages and `data/*.json` are network first with the saved copy as fallback; other files are served from
  the cache and refreshed in the background. The cache name changes with every build.
- `cards/<slug>.jpg`: a 1200 x 630 share card per kindergarten (name, district and up to three key figures), used as
  `og:image` on `b/<slug>/`. Sharing a kindergarten from the app links to that page. Cards are re-rendered only when
  their content changes (`cards/index.json` holds a hash per card).
- Bike mode: the ranking uses an estimate calibrated against Entur's bike routes (about 5.75 min per straight-line km
  plus 6 min). On a kindergarten's page the app asks Entur's journey planner for the actual bike or walking route and
  draws it on the map. Only on the public site; the artifact cannot call other hosts.

## Data sources

| Source | Used for | License |
|---|---|---|
| [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, via [Protomaps](https://protomaps.com) | Map tiles, nature, roads, place names, kindergarten areas | ODbL 1.0 |
| [Kartverket](https://www.kartverket.no), Matrikkelen eiendomskart teig and kommuneinfo | Kindergarten plots, outdoor area and municipal borders | CC BY 4.0 |
| [Entur](https://developer.entur.no) | Public transport stops and lines | NLOD |
| [Udir](https://www.udir.no) — Barnehagefakta, statistikkportalen and the national school register (NSR) | Parent survey, staffing, schools | NLOD 2.0 |
| [Oslo kommune](https://www.oslo.kommune.no), [Bærum kommune](https://www.baerum.kommune.no), [Asker](https://www.asker.kommune.no), [Lillestrøm](https://www.lillestrom.kommune.no), [Lørenskog](https://www.lorenskog.kommune.no) and [Nordre Follo](https://www.nordrefollo.kommune.no) kommune | Prices, food, phone, vacancies (Oslo), descriptions | See note below |
| [Noto](https://notofonts.github.io) fonts | Map labels | SIL OFL 1.1 (`map/f/OFL.txt`) |

The kindergarten descriptions ("Om barnehagen", "Slik jobber vi") come from each kindergarten's page on the municipality's website. They belong to the kindergartens and the municipalities and are not covered by any license in this repository.

## License

Copyright © 2026 Joachim Milling. All rights reserved.

The code is public so the site can be served from GitHub Pages. It is not licensed for reuse. Third-party data keeps its own license, listed above.
