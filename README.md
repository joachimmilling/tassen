# Tassen

Find, compare and prioritize kindergartens (barnehager) in Oslo and Bærum.

**Live:** https://joachimmilling.github.io/tassen/

The app itself is in Norwegian. It is one static page, `index.html`, which loads map tiles, fonts and kindergarten texts from `map/` when they are needed. MapLibre GL JS is loaded from jsDelivr.

For search engines, every kindergarten also has a small static page in `b/<slug>/` and every district one in `d/<slug>/`. They hold the key facts and link into the app (`#<slug>` opens that kindergarten). `sitemap.xml` lists all pages, and `og.png` is the image shown when a link is shared.

## Data sources

| Source | Used for | License |
|---|---|---|
| [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, via [Protomaps](https://protomaps.com) | Map tiles, nature, roads, place names, kindergarten areas | ODbL 1.0 |
| [Kartverket](https://www.kartverket.no), Matrikkelen eiendomskart teig | Kindergarten plots and outdoor area | CC BY 4.0 |
| [Entur](https://developer.entur.no) | Public transport stops and lines | NLOD |
| [Udir](https://www.udir.no) — Barnehagefakta and the national school register (NSR) | Parent survey, staffing, schools | NLOD 2.0 |
| [Oslo kommune](https://www.oslo.kommune.no) and [Bærum kommune](https://www.baerum.kommune.no) | Prices, food, vacancies, descriptions | See note below |
| [Noto](https://notofonts.github.io) fonts | Map labels | SIL OFL 1.1 (`map/f/OFL.txt`) |

The kindergarten descriptions ("Om barnehagen", "Slik jobber vi") come from each kindergarten's page on oslo.kommune.no and baerum.kommune.no. They belong to the kindergartens and the municipalities and are not covered by any license in this repository.

## License

Copyright © 2026 Joachim Milling. All rights reserved.

The code is public so the site can be served from GitHub Pages. It is not licensed for reuse. Third-party data keeps its own license, listed above.
