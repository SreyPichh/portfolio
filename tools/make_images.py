#!/usr/bin/env python3
"""Render the two picture files the site needs, using Google Chrome in the background.

    python3 tools/build.py --serve      # in one terminal (the share image is a photo of the home page)
    python3 tools/make_images.py        # in another

Writes into src/static/ (then rebuild, or let --serve pick it up):
    apple-touch-icon.png   180 x 180, from favicon.svg (the icon phones use for bookmarks)
    og-image.png           1200 x 630, a picture of the home page (the preview when the link is shared)

Run it again after you change your name in site.json, so the share image shows it.
"""
import os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC = os.path.join(ROOT, 'src', 'static')
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5173/'

CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    shutil.which('google-chrome') or '', shutil.which('chromium') or '', shutil.which('chromium-browser') or '',
]
chrome = next((c for c in CANDIDATES if c and os.path.exists(c)), None)
if not chrome:
    sys.exit('Google Chrome was not found. Install it, or make the two images by hand (sizes are listed above).')


def shoot(target, out, w, h, wait_ms=4000):
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([
            chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--mute-audio',
            '--no-first-run', '--no-default-browser-check', f'--user-data-dir={profile}',
            f'--window-size={w},{h}', f'--virtual-time-budget={wait_ms}', '--force-device-scale-factor=1',
            f'--screenshot={out}', target,
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    print('wrote', os.path.relpath(out, ROOT))


# 1) the touch icon: the favicon drawn at 180 px on its cream tile
with tempfile.TemporaryDirectory() as tmp:
    page = os.path.join(tmp, 'icon.html')
    svg = open(os.path.join(STATIC, 'favicon.svg'), encoding='utf-8').read()
    svg = svg.replace('<svg ', '<svg width="180" height="180" ', 1).replace('rx="14"', 'rx="0"', 1)
    with open(page, 'w', encoding='utf-8') as f:
        f.write(f'<!doctype html><html><body style="margin:0;background:#FAF7F0">{svg}</body></html>')
    shoot('file://' + page, os.path.join(STATIC, 'apple-touch-icon.png'), 180, 180, 500)

# 2) the share image: the home page at 1200 x 630
try:
    import urllib.request
    urllib.request.urlopen(URL, timeout=3)
except Exception:
    sys.exit(f'Could not open {URL}. Start the site first: python3 tools/build.py --serve')
shoot(URL, os.path.join(STATIC, 'og-image.png'), 1200, 630)
