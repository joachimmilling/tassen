#!/usr/bin/env python3
"""Update the list of open kindergarten places in Oslo for the Tassen site.

Source: https://github.com/torkilv/ledige-barnehageplasser-oslo collects the vacancy lists that
Oslo's districts publish on oslo.kommune.no and stores them in docs/data.json several times a day.

This script parses that file, matches each kindergarten to Tassen's own list (data/kindergartens.json)
and writes:
  data/vacancies.json                        read by the app on the published site
  r/ledige-barnehageplasser-oslo/index.html  the list section, the date line and dateModified
  vacancies.xml                              RSS feed with one item per new or changed vacancy

Usage: update_vacancies.py <source data.json> <repo root> [--force]
--force rewrites the outputs even when the data has not changed (used by the site build).
It runs daily in .github/workflows/update-vacancies.yml and once during the site build.
The page text is Norwegian because the site is; everything else is English.
"""
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import unicodedata

BASE = "https://joachimmilling.github.io/tassen/"
PAGE = "r/ledige-barnehageplasser-oslo/"
MONTHS = ["januar", "februar", "mars", "april", "mai", "juni", "juli", "august", "september", "oktober", "november", "desember"]
UNDER = re.compile(r"(\d+)\s*(?:ledige?\s+)?(?:småbarnsplass(?:er)?|plass(?:er)?(?:\s+for\s+barn)?\s+under\s+3)", re.I)
OVER = re.compile(r"(\d+)\s*(?:ledige?\s+)?plass(?:er)?(?:\s+for\s+barn)?\s+over\s+3", re.I)
FROM = re.compile(r"ledig\s+fra\s+(.+?)\.?\s*$", re.I)
# A new entry starts where a capitalised name directly follows the end of the previous one ("…novemberFurustien barnehage: …")
SPLIT = re.compile(r"(?<=[a-zæøå0-9.)])(?=[A-ZÆØÅ][^:]{2,80}:\s)")


def norm(name):
    s = unicodedata.normalize("NFKD", name.lower().replace("æ", "ae").replace("ø", "o").replace("å", "a"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\b(barnehage|barnehave|bhg|as|sa|da|avd|avdeling)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def parse(source):
    """Return {district: {name: {"u": int, "o": int, "fra": str}}} from the source file."""
    out = {}
    for district, value in (source.get("spots") or {}).items():
        texts = value.get("available_spots") if isinstance(value, dict) else value
        if isinstance(texts, str):
            texts = [texts]
        entries = {}
        for text in texts or []:
            for part in SPLIT.split(str(text)):
                if ":" not in part:
                    continue
                name, rest = part.split(":", 1)
                name = re.sub(r"\s+", " ", name).strip()
                u = sum(int(x) for x in UNDER.findall(rest))
                o = sum(int(x) for x in OVER.findall(rest))
                if not name or not (u or o):
                    continue
                m = FROM.search(rest.strip())
                entry = {"u": u, "o": o}
                if m:
                    entry["fra"] = m.group(1).strip()
                entries[name] = entry
        if entries:
            out[district] = entries
    return out


def match(names, kindergartens):
    exact = {k["n"]: k for k in kindergartens}
    loose = {}
    for k in kindergartens:
        loose.setdefault(norm(k["n"]), k)
    return {n: exact.get(n) or loose.get(norm(n)) for n in names}


def date_no(d):
    return f"{d.day}. {MONTHS[d.month - 1]} {d.year}"


def spots_text(e):
    parts = []
    if e["u"]:
        parts.append(f"{e['u']} {'plass' if e['u'] == 1 else 'plasser'} under 3 år")
    if e["o"]:
        parts.append(f"{e['o']} {'plass' if e['o'] == 1 else 'plasser'} over 3 år")
    return " og ".join(parts) + (f", ledig fra {e['fra']}" if e.get("fra") else "")


def render_section(by_district, kg_of, updated):
    esc = html.escape
    total = sum(e["u"] + e["o"] for d in by_district.values() for e in d.values())
    n_kg = sum(len(d) for d in by_district.values())
    parts = [
        '<div class="stats">'
        f'<div class="stat"><b>{total}</b><span>ledige plasser</span></div>'
        f'<div class="stat"><b>{n_kg}</b><span>barnehager</span></div>'
        f'<div class="stat"><b>{len(by_district)}</b><span>bydeler med liste</span></div></div>',
        f'<p class="sub">Kilden ble sist oppdatert {date_no(updated)}. Listen dekker bydelene som publiserer ledige plasser på Oslo kommunes sider: '
        f'{esc(", ".join(sorted(by_district)))}.</p>',
    ]
    if not by_district:
        parts.append("<p>Ingen bydeler har meldt ledige plasser akkurat nå.</p>")
    for district in sorted(by_district):
        rows = []
        for name, e in sorted(by_district[district].items(), key=lambda x: x[0].lower()):
            k = kg_of.get(name)
            label = f'<a href="../../b/{esc(k["slug"])}/">{esc(k["n"])}</a>' if k else esc(name)
            rows.append(f'<div class="row"><span class="k">{label}<small>{esc(spots_text(e))}</small></span><span class="v">{e["u"] + e["o"]}</span></div>')
        parts.append(f'<h3>{esc(district)}</h3><div class="list">{"".join(rows)}</div>')
    return "\n".join(parts)


def rss(items, updated):
    esc = html.escape
    now = dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>',
           "<title>Ledige barnehageplasser i Oslo · Tassen</title>", f"<link>{BASE}{PAGE}</link>",
           f'<atom:link href="{BASE}vacancies.xml" rel="self" type="application/rss+xml"/>',
           "<description>Nye ledige plasser i barnehagene i Oslo, fra bydelenes lister. Oppdateres daglig.</description>",
           "<language>nb</language>", f"<lastBuildDate>{now}</lastBuildDate>"]
    for it in items:
        out.append("<item>"
                   f"<title>{esc(it['title'])}</title><link>{esc(it['link'])}</link>"
                   f"<description>{esc(it['text'])}</description>"
                   f'<guid isPermaLink="false">{it["guid"]}</guid><pubDate>{it["date"]}</pubDate></item>')
    out.append("</channel></rss>")
    return "\n".join(out)


def main(src_path, repo, force=False):
    source = json.load(open(src_path, encoding="utf-8"))
    # the list is Oslo's, so only Oslo kindergartens can match (other municipalities have kindergartens with the same names)
    kindergartens = [k for k in json.load(open(os.path.join(repo, "data", "kindergartens.json"), encoding="utf-8")) if k.get("ko", "Oslo") == "Oslo"]
    by_district = parse(source)
    if not by_district:
        print("No vacancies parsed; keeping the previous data.")
        return 0
    updated = dt.datetime.fromisoformat(str(source.get("lastUpdate", "")).replace("Z", "")[:19] or dt.datetime.now().isoformat()[:19])
    kg_of = match([n for d in by_district.values() for n in d], kindergartens)

    vac_path = os.path.join(repo, "data", "vacancies.json")
    try:
        previous = json.load(open(vac_path, encoding="utf-8"))
    except (OSError, ValueError):
        previous = {}
    seen = previous.get("seen", {})
    today = dt.date.today().isoformat()

    by_id, items, current = {}, [], {}
    for district, entries in by_district.items():
        for name, e in entries.items():
            k = kg_of.get(name)
            if k:
                by_id[str(k["id"])] = e
            guid = hashlib.sha1(json.dumps([name, e], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
            current[guid] = seen.get(guid, today)
            first = dt.datetime.fromisoformat(current[guid]).replace(hour=6, tzinfo=dt.timezone.utc)
            items.append({"guid": guid, "title": f"Ledig plass: {k['n'] if k else name} ({district})", "text": spots_text(e) + ".",
                          "link": f"{BASE}b/{k['slug']}/" if k else f"{BASE}{PAGE}", "date": first.strftime("%a, %d %b %Y %H:%M:%S +0000"), "_d": current[guid]})
    items.sort(key=lambda x: (x["_d"], x["title"]), reverse=True)

    data = {"updated": updated.isoformat(), "source": "https://github.com/torkilv/ledige-barnehageplasser-oslo",
            "byId": by_id, "byDistrict": by_district, "unmatched": sorted(n for n, k in kg_of.items() if not k), "seen": current}
    os.makedirs(os.path.dirname(vac_path), exist_ok=True)
    if not force and {x: data[x] for x in ("updated", "byDistrict")} == {x: previous.get(x) for x in ("updated", "byDistrict")} and previous.get("seen") == current:
        print("No change.")
        return 0
    json.dump(data, open(vac_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    open(os.path.join(repo, "vacancies.xml"), "w", encoding="utf-8").write(rss(items, updated))

    page_path = os.path.join(repo, PAGE, "index.html")
    if os.path.exists(page_path):
        page = open(page_path, encoding="utf-8").read()
        section = render_section(by_district, kg_of, updated)
        page = re.sub(r"<!--vacancies-->.*?<!--/vacancies-->", lambda _: f"<!--vacancies-->{section}<!--/vacancies-->", page, flags=re.S)
        page = re.sub(r'(<p class="byline">Tassen · Oppdatert )[^<]*(</p>)', lambda m: m.group(1) + date_no(dt.date.today()) + m.group(2), page)
        page = re.sub(r'("dateModified": ")[0-9-]+(")', lambda m: m.group(1) + today + m.group(2), page)
        open(page_path, "w", encoding="utf-8").write(page)
    n = sum(len(d) for d in by_district.values())
    print(f"{n} kindergartens with open places in {len(by_district)} districts; {len(data['unmatched'])} not matched.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], "--force" in sys.argv[3:]))
