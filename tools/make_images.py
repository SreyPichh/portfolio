#!/usr/bin/env python3
"""Render the two picture files the site needs, using Google Chrome in the background.

    python3 tools/build.py --serve      # in one terminal (the share image is a photo of the home page)
    python3 tools/make_images.py        # in another

Writes into src/static/ (then rebuild, or let --serve pick it up):
    apple-touch-icon.png   180 x 180, from favicon.svg (the icon phones use for bookmarks)
    og-image.png           1200 x 630, a picture of the home page (the preview when the link is shared)
    assets/desk-photo.jpg  900 x 900, a close-up of the office desk for the polaroid on the Notes page

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

# 2) the "photo" of the desk for the polaroid on the Notes page: a close-up of the office drawing
def desk_photo(base_url, out, box=(548, 360, 440, 440), size=900):
    """Cut the desk corner out of the room drawing, lit as it is by day, and save it as a square photo."""
    import json, re, urllib.request
    html = urllib.request.urlopen(base_url, timeout=5).read().decode('utf-8')
    defs = re.search(r'<!-- Shared drawings -->\s*(<svg width="0".*?</svg>)', html, re.S).group(1)
    room = re.search(r'(<svg class="room".*?</svg>)\s*</div>', html, re.S).group(1)
    room = re.sub(r'viewBox="[^"]*"', f'viewBox="{box[0]} {box[1]} {box[2]} {box[3]}"', room, count=1)
    room = re.sub(r'preserveAspectRatio="[^"]*"', 'preserveAspectRatio="xMidYMid slice"', room, count=1)
    # the daytime look that script.js would normally set (the wall colours come from the .office wrapper)
    keys = ['sky-1','sky-2','sky-3','mount-1','mount-2','hb-1','hb-2','hm-1','hm-2','hf-1','hf-2','tree','tree-2','cloud','cloud-shade','sun','sun-edge','glow']
    day = ['#8FBCE8','#C4DEF3','#F1EEE4','#C3D5EA','#DFE8EE','#CFE3B6','#B2D198','#A6CC88','#8ABA6E','#8BBD6B','#6CA155','#5A8C55','#46733F','#FFFFFF','#DCE7F2','#FFF1C4','#FFD98C','#FFF6DA']
    vars_ = ';'.join(f'--{k}:{v}' for k, v in zip(keys, day)) + ';--tint:#fff;--dark:0;--beam:.95;--lamp:.18;--lamp-vis:0;--stars:0;--moon:0'
    page = f'''<!doctype html><html data-theme="day" style="{vars_}"><head><meta charset="utf-8">
<link rel="stylesheet" href="{base_url.rstrip('/')}/styles.css">
<style>html,body{{margin:0;background:#F2EEE6;overflow:hidden}} .room{{width:{size}px!important;height:{size}px!important;min-width:0!important}}
*{{animation:none!important;transition:none!important}} .office{{min-height:0!important}}</style></head><body>{defs}<div class="office">{room}</div></body></html>'''
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, 'desk.html'); png = os.path.join(tmp, 'desk.png')
        open(f, 'w', encoding='utf-8').write(page)
        shoot('file://' + f, png, size, size, 2500)
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '82', png, '--out', out], check=True, stdout=subprocess.DEVNULL)
    print('wrote', os.path.relpath(out, ROOT))


# 3) the share image: the home page at 1200 x 630
try:
    import urllib.request
    urllib.request.urlopen(URL, timeout=3)
except Exception:
    sys.exit(f'Could not open {URL}. Start the site first: python3 tools/build.py --serve')
shoot(URL, os.path.join(STATIC, 'og-image.png'), 1200, 630)
desk_photo(URL, os.path.join(STATIC, 'assets', 'desk-photo.jpg'))
