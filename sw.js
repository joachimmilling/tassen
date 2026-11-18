/* Tassen service worker: keeps the app and what it has fetched, so it opens and visit mode works without a connection.
   Pages and data files: network first, with the saved copy as fallback. Other files on the site and the map library:
   the saved copy first, refreshed in the background. Other hosts (such as Entur's routes) are never stored. */
const V = "tassen-e1e2fb8aef";
const CORE = ["./", "en/", "map/texts.json", "map/plots.json", "manifest.webmanifest", "icon-192.png"];
const ROOT = new URL("./", self.location).pathname;
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).catch(() => {})); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith("tassen-") && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
async function trim(c) { const ks = await c.keys(); for (let i = 0; i < ks.length - 500; i++) await c.delete(ks[i]); }
const keep = (c, req, res) => { if (res && (res.ok || res.type === "opaque")) { c.put(req, res.clone()); trim(c); } return res; };
self.addEventListener("fetch", e => {
  const req = e.request; if (req.method !== "GET") return;
  const u = new URL(req.url), mine = u.origin === self.location.origin && u.pathname.startsWith(ROOT), lib = u.hostname === "cdn.jsdelivr.net";
  if (!mine && !lib) return;
  if (req.mode === "navigate" || (mine && /\/data\/[^/]+\.json$/.test(u.pathname))) {
    e.respondWith(caches.open(V).then(c => fetch(req).then(res => keep(c, req, res)).catch(() => c.match(req, { ignoreSearch: true }).then(m => m || (req.mode === "navigate" ? c.match(ROOT) : undefined)))));
    return;
  }
  e.respondWith(caches.open(V).then(async c => { const hit = await c.match(req); const net = fetch(req).then(res => keep(c, req, res)).catch(() => hit); return hit || net; }));
});
