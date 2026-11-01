#!/usr/bin/env python3
"""Build FM-1 Pocket: the installable site (repo root) and the claude.ai artifact page.
Usage: python3 build/build.py [artifact-output.html]"""
import base64, hashlib, pathlib, subprocess, sys
here = pathlib.Path(__file__).resolve().parent
root = here.parent
t = (here / 'template.html').read_text()
t = t.replace('__WASM__', base64.b64encode((here / 'simulator.wasm').read_bytes()).decode())
t = t.replace('__SVG__', 'data:image/svg+xml;base64,' + base64.b64encode((here / 'faceplate.svg').read_bytes()).decode())

if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(t)

split = t.index('<div id="fit">')
head, body = t[:split], t[split:]
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="FM-1">
<meta name="theme-color" content="#0d0d0d">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<style>*{{box-sizing:border-box}}body{{margin:0}}[hidden]{{display:none!important}}</style>
{head}</head>
<body>
{body}
<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{{}}));</script>
</body>
</html>
'''
(root / 'index.html').write_text(page)

for size in (180, 192, 512):
    subprocess.run(['rsvg-convert', '-w', str(size), '-h', str(size), str(here / 'icon.svg'),
                    '-o', str(root / f'icon-{size}.png')], check=True)

(root / 'manifest.webmanifest').write_text('''{
  "name": "FM-1 Pocket",
  "short_name": "FM-1",
  "start_url": "./",
  "scope": "./",
  "display": "fullscreen",
  "orientation": "landscape",
  "background_color": "#0d0d0d",
  "theme_color": "#0d0d0d",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}
  ]
}
''')

# Play together: the peer-to-peer library is loaded only when a session starts.
trystero = (here / 'trystero.js').read_bytes()
(root / 'trystero.js').write_bytes(trystero)

# The cache name changes whenever the page changes, so installed copies pick up new builds.
version = hashlib.sha256(page.encode() + trystero).hexdigest()[:12]
(root / 'sw.js').write_text(f'''const CACHE = 'fm1-pocket-{version}';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png', './trystero.js'];
self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});
// Serve from the cache so it works offline; refresh the cache in the background when online.
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE).then(async cache => {{
    const hit = await cache.match(e.request, {{ignoreSearch: true}});
    const net = fetch(e.request).then(r => {{ if (r.ok) cache.put(e.request, r.clone()); return r; }}).catch(() => hit);
    return hit || net;
  }}));
}});
''')
print('built', root / 'index.html', 'cache', version)
