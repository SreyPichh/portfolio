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
