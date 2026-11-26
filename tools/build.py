#!/usr/bin/env python3
"""Build the portfolio into dist/, ready to upload to any static host.

    python3 tools/build.py            # build once into ./dist
    python3 tools/build.py --serve    # build, serve on http://localhost:5173 and rebuild on every save
    python3 tools/build.py --check    # list the placeholders still waiting for your words

Where things live:
    site.json        your name, email, links (one place)
    src/pages/       one file per page; the lines between --- at the top set its title and description
    src/partials/    pieces shared by every page (layout, top bar, drawings, story dialog)
    src/static/      copied as-is: styles.css, script.js, assets/, icons, share image

Inside pages and partials:
    {{site.name}}         a value from site.json (dots reach inside: {{site.socials.linkedin}})
    {{page.title}}        a value from the page's --- block
    {{> topbar}}          pastes src/partials/topbar.html
Only the Python standard library is used, so any host with Python 3 can run it.
"""
import html, http.server, json, os, re, shutil, socketserver, sys, threading, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
DIST = os.path.join(ROOT, 'dist')
TOKEN = re.compile(r'\{\{\s*(>\s*)?([\w.]+)\s*\}\}')
NAV = ('about', 'work', 'notes', 'contact')
# social links in site.json, in the order they appear, drawn as little postage stamps
NETWORKS = [  # key, label, the letters on the stamp (used when there's no logo), stamp colour
    ('linkedin', 'LinkedIn', 'in', '#CFE0F6'), ('instagram', 'Instagram', 'ig', '#F6D3DD'),
    ('facebook', 'Facebook', 'fb', '#D6DDF5'), ('telegram', 'Telegram', 'tg', '#CFEAF2'),
    ('behance', 'Behance', 'Bē', '#E2DAF5'), ('github', 'GitHub', 'gh', '#E6E2D8'), ('readcv', 'Read.cv', 'cv', '#DCE9CF'),
]
# the networks' own logos, drawn on a 24 x 24 grid
LOGOS = {
    'linkedin': '<rect width="24" height="24" rx="5" fill="#0A66C2"/><path fill="#fff" d="M6.2 9.6h2.9v8.8H6.2zM7.65 5.4a1.68 1.68 0 1 1 0 3.36 1.68 1.68 0 0 1 0-3.36zM10.9 9.6h2.8v1.2h.04c.39-.74 1.34-1.52 2.76-1.52 2.95 0 3.5 1.94 3.5 4.47v4.65h-2.9v-4.12c0-.98-.02-2.25-1.37-2.25-1.37 0-1.58 1.07-1.58 2.18v4.19h-2.9z"/>',
    'instagram': '<defs><radialGradient id="igGlow" cx=".3" cy="1.07" r="1.2"><stop offset="0" stop-color="#FFD776"/><stop offset=".25" stop-color="#F3A554"/><stop offset=".5" stop-color="#F15C4A"/><stop offset=".75" stop-color="#C22F8E"/><stop offset="1" stop-color="#7B3BC6"/></radialGradient></defs>'
                 '<rect width="24" height="24" rx="6" fill="url(#igGlow)"/><rect x="5" y="5" width="14" height="14" rx="4.2" fill="none" stroke="#fff" stroke-width="1.8"/><circle cx="12" cy="12" r="3.3" fill="none" stroke="#fff" stroke-width="1.8"/><circle cx="16.4" cy="7.6" r="1.1" fill="#fff"/>',
    'facebook': '<circle cx="12" cy="12" r="12" fill="#1877F2"/><path fill="#fff" d="M13.4 24v-8.6h2.9l.44-3.4H13.4V9.9c0-.98.27-1.65 1.68-1.65h1.8V5.2a24 24 0 0 0-2.6-.13c-2.58 0-4.35 1.58-4.35 4.47V12H7.02v3.4h2.91V24z"/>',
    'telegram': '<circle cx="12" cy="12" r="12" fill="#29A9EB"/><path fill="#fff" d="M5.5 11.7l11.2-4.3c.52-.19.97.13.8.92l-1.9 9c-.14.63-.52.79-1.05.49l-2.9-2.14-1.4 1.35c-.15.15-.29.29-.59.29l.21-2.95 5.37-4.85c.23-.21-.05-.32-.36-.12l-6.64 4.18-2.86-.89c-.62-.2-.63-.62.13-.92z"/>',
}


def social_links(site):
    """The social links that have a URL, as (key, label, letters, colour, url)."""
    links = site.get('socials') or {}
    return [(key, label, mark, col, links[key].strip()) for key, label, mark, col in NETWORKS
            if isinstance(links.get(key), str) and links[key].strip() not in ('', '#')]


def stamps_html(site):
    """The "Or find me elsewhere" stamps on the contact page, or nothing when there are no links."""
    links = social_links(site)
    if not links:
        return ''
    tilt = ['-4deg', '3deg', '-2deg', '2.5deg', '-3deg']
    face = lambda key, mark: (f'<svg class="stamp-logo" viewBox="0 0 24 24" aria-hidden="true">{LOGOS[key]}</svg>' if key in LOGOS
                              else f'<b>{html.escape(mark)}</b>')
    items = ''.join(
        f'\n            <li><a class="stamp-link" href="{html.escape(url)}" target="_blank" rel="noopener" style="--art:{col};--r:{tilt[i % len(tilt)]}">'
        f'<span class="stamp-in">{face(key, mark)}<span class="mono">{html.escape(label)}</span></span></a></li>'
        for i, (key, label, mark, col, url) in enumerate(links))
    return ('<nav class="elsewhere reveal" aria-label="Elsewhere">\n          <p class="mono">Or find me elsewhere</p>\n'
            f'          <ul class="stamps">{items}\n          </ul>\n        </nav>')


class BuildError(Exception):
    pass


def read(*parts):
    with open(os.path.join(*parts), encoding='utf-8') as f:
        return f.read()


def front_matter(text, name):
    """Split the --- block off the top of a page."""
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        raise BuildError(f'{name}: needs a --- block at the top with title and description')
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, _, v = line.partition(':')
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def lookup(ctx, key, where):
    cur = ctx
    for part in key.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            raise BuildError(f'{where}: unknown {{{{{key}}}}}')
        cur = cur[part]
    return cur


def render(text, ctx, raw, where, depth=0):
    """Fill {{tokens}} and {{> partials}}. Values from site.json are HTML-escaped."""
    if depth > 8:
        raise BuildError(f'{where}: partials include each other in a loop')

    def fill(m):
        is_partial, key = m.group(1), m.group(2)
        if is_partial:
            path = os.path.join(SRC, 'partials', key + '.html')
            if not os.path.exists(path):
                raise BuildError(f'{where}: no partial called {key} (looked for src/partials/{key}.html)')
            return render(read(path), ctx, raw, f'partials/{key}.html', depth + 1)
        if key in raw:
            return raw[key]
        val = lookup(ctx, key, where)
        if isinstance(val, (dict, list)):
            raise BuildError(f'{where}: {{{{{key}}}}} is a group, pick one item inside it')
        return html.escape(str(val), quote=True)

    return TOKEN.sub(fill, text)


def load_site():
    try:
        site = json.loads(read(ROOT, 'site.json'))
    except json.JSONDecodeError as e:
        raise BuildError(f'site.json: {e.msg} on line {e.lineno} (check for a missing comma or quote)')
    site['url'] = site.get('url', '').rstrip('/')
    site['first'] = (site.get('first') or site.get('name', '').split(' ')[0]).strip()
    base = site.get('basePath') or '/'
    site['basePath'] = '/' + base.strip('/') + '/' if base.strip('/') else '/'
    return site


def build():
    t0 = time.time()
    site = load_site()
    mono = site.get('monogram') or site['name'][:2]
    stamp = str(int(t0))

    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(os.path.join(SRC, 'static'), DIST, ignore=shutil.ignore_patterns('.DS_Store'))

    layout = read(SRC, 'partials', 'layout.html')
    pages_dir = os.path.join(SRC, 'pages')
    built = []
    for fname in sorted(os.listdir(pages_dir)):
        if not fname.endswith('.html'):
            continue
        meta, body = front_matter(read(pages_dir, fname), f'pages/{fname}')
        for need in ('title', 'description'):
            if need not in meta:
                raise BuildError(f'pages/{fname}: the --- block needs a {need}: line')
        ctx = {'site': site}
        # titles and descriptions may use {{site.name}} too
        page = {k: html.unescape(render(v, ctx, {}, f'pages/{fname}')) for k, v in meta.items()}
        path = '' if fname == 'index.html' else fname
        page['url'] = f"{site['url']}/{path}"
        ctx['page'] = page
        is_404 = fname == '404.html'
        raw = {
            'mark': html.escape(mono[:1]) + '<em>' + html.escape(mono[1:]) + '</em>',
            'build': stamp,
            'socials': stamps_html(site),
            # the 404 page can be shown at any address, so its links start from the site root
            'page.base': f'<base href="{html.escape(site["basePath"])}">' if is_404 else '',
        }
        for n in NAV:
            raw['nav.' + n] = ' aria-current="page"' if page.get('nav') == n else ''
        raw['content'] = render(body, ctx, raw, f'pages/{fname}').strip('\n') + '\n'
        out = render(layout, ctx, raw, 'partials/layout.html')
        out = re.sub(r'\n[ \t]*\n(?=[ \t]*<link rel="canonical")', '\n', out)  # drop the blank base line
        with open(os.path.join(DIST, fname), 'w', encoding='utf-8') as f:
            f.write(out)
        if not is_404 and page.get('sitemap', 'yes') != 'no':
            built.append(path)

    # search engines: a sitemap and a robots file pointing at it
    if site['url']:
        urls = '\n'.join(f'  <url><loc>{html.escape(site["url"])}/{p}</loc></url>' for p in built)
        with open(os.path.join(DIST, 'sitemap.xml'), 'w') as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
        with open(os.path.join(DIST, 'robots.txt'), 'w') as f:
            f.write(f'User-agent: *\nAllow: /\n\nSitemap: {site["url"]}/sitemap.xml\n')

    print(f'built {len(built) + (1 if os.path.exists(os.path.join(pages_dir, "404.html")) else 0)} pages into dist/ in {time.time() - t0:.2f}s', flush=True)


def snapshot():
    """Modification times of everything the build reads."""
    seen = {}
    for base in (SRC,):
        for d, _, files in os.walk(base):
            for f in files:
                p = os.path.join(d, f)
                seen[p] = os.path.getmtime(p)
    seen['site.json'] = os.path.getmtime(os.path.join(ROOT, 'site.json'))
    return seen


def serve(port=5173):
    def safe_build():
        try:
            build()
        except BuildError as e:
            print('build failed:', e, flush=True)
        except Exception as e:  # keep serving; the next save tries again
            print(f'build failed: {type(e).__name__}: {e}', flush=True)

    safe_build()

    def watch():
        last = snapshot()
        while True:
            time.sleep(0.5)
            now = snapshot()
            if now != last:
                last = now
                safe_build()

    threading.Thread(target=watch, daemon=True).start()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=DIST, **kw)

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')  # always see the latest build while editing
            super().end_headers()

        def send_error(self, code, message=None, explain=None):
            page = os.path.join(DIST, '404.html')
            if code == 404 and os.path.exists(page):  # behave like the real host
                body = open(page, 'rb').read()
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                if self.command != 'HEAD':
                    self.wfile.write(body)
                return
            super().send_error(code, message, explain)

        def log_message(self, *a):
            pass

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(('127.0.0.1', port), Handler) as httpd:
        print(f'serving http://localhost:{port}  (edits rebuild automatically; Ctrl+C to stop)', flush=True)
        httpd.serve_forever()


PLACEHOLDER = re.compile(r'\[[A-Z][^\]\n<>{}=;/*]{1,90}\]')
DEFAULTS = {'name': 'Your Name', 'email': 'hello@yourname.com', 'url': 'https://yourname.com'}


def check():
    """List what still needs filling in before launch."""
    site = load_site()
    todo = []
    def walk(d, prefix=''):
        for k, v in d.items():
            if k.startswith('_'):
                continue
            if isinstance(v, dict):
                walk(v, prefix + k + '.')
            elif prefix == 'socials.':
                continue  # an empty link is simply hidden
            elif isinstance(v, str) and ('[' in v or v == '#' or v == DEFAULTS.get(k)):
                todo.append(f'site.json  {prefix}{k}: {v!r}')
    walk(site)
    if not site.get('resume'):
        todo.append('site.json  resume: empty (the "Download résumé" button shows a reminder instead)')
    if not site.get('playlist'):
        todo.append('site.json  playlist: empty (link to your Spotify or Apple Music playlist)')
    files = [os.path.join('src', 'pages', f) for f in sorted(os.listdir(os.path.join(SRC, 'pages'))) if f.endswith('.html')]
    files.append(os.path.join('src', 'static', 'script.js'))
    for rel in files:
        for n, line in enumerate(read(ROOT, rel).splitlines(), 1):
            for m in PLACEHOLDER.finditer(line):
                todo.append(f'{rel}:{n}  {m.group(0)[:70]}')
    for line in todo:
        print(line)
    print(f'\n{len(todo)} thing(s) left to fill in' if todo else 'Nothing left to fill in.')


if __name__ == '__main__':
    try:
        if '--serve' in sys.argv:
            serve()
        elif '--check' in sys.argv:
            check()
        else:
            build()
    except BuildError as e:
        sys.exit(f'build failed: {e}')
    except KeyboardInterrupt:
        pass
