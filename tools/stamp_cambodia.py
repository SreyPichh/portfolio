#!/usr/bin/env python3
"""Draw the Cambodia postage stamp on the Contact page's envelope: Angkor Wat printed in red over
fine concentric circles, birds, and the name in English and Khmer.

    python3 tools/stamp_cambodia.py            # prints the SVG
    python3 tools/stamp_cambodia.py --write    # puts it into src/pages/contact.html

The temple is drawn from simple shapes (five lotus-bud towers, the colonnaded gallery, the terrace
and steps, a hint of its reflection), so it's an original drawing.
"""
import math
import os
import random
import sys

W, H = 120, 150
RED, INK, PAPER = '#C8102E', '#1E1E1E', '#FBF9F4'
rnd = random.Random(7)


def tower(cx, base, w, h):
    """A lotus-bud tower built the way Angkor's are: stacked tiers that bulge a little, then narrow
    to a point, each tier with knobbly ends, on a plinth with a doorway."""
    parts, n = [], 8
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        y0, y1 = base - h * t0, base - h * t1
        bulge = lambda t: w / 2 * (1 - t ** 1.7) * (1 + .18 * math.sin(math.pi * min(t * 2.2, 1)))
        half = bulge(t0)
        parts.append(f'<rect x="{cx - half:.2f}" y="{y1:.2f}" width="{2 * half:.2f}" height="{y0 - y1 + .35:.2f}" rx="{min(half, .9):.2f}" fill="{RED}"/>')
        r = max(.35, w * .07 * (1 - t0))
        parts.append(f'<circle cx="{cx - half:.2f}" cy="{y1 + .4:.2f}" r="{r:.2f}" fill="{RED}"/><circle cx="{cx + half:.2f}" cy="{y1 + .4:.2f}" r="{r:.2f}" fill="{RED}"/>')
        if 0 < k < n - 1:
            parts.append(f'<path d="M{cx - half * .7:.2f} {y0 - .2:.2f} H{cx + half * .7:.2f}" stroke="{PAPER}" stroke-width=".4" opacity=".85"/>')
    top = base - h
    parts.append(f'<path d="M{cx - .9:.2f} {top + .6:.2f} Q{cx:.2f} {top - 3.4:.2f} {cx + .9:.2f} {top + .6:.2f}Z" fill="{RED}"/>')
    parts.append(f'<rect x="{cx - w * .62:.2f}" y="{base - .2:.2f}" width="{w * 1.24:.2f}" height="4.4" fill="{RED}"/>')
    parts.append(f'<path d="M{cx - 1.2:.2f} {base + 4.2:.2f} V{base + 1.6:.2f} Q{cx:.2f} {base + .3:.2f} {cx + 1.2:.2f} {base + 1.6:.2f} V{base + 4.2:.2f}Z" fill="{PAPER}"/>')
    return ''.join(parts)


def bird(x, y, s, tilt):
    return (f'<path transform="translate({x} {y}) rotate({tilt}) scale({s})" '
            f'd="M-6 0 Q-3 -2.6 0 .4 Q3 -2.6 6 0 Q3 -1 0 1.8 Q-3 -1 -6 0Z" fill="{RED}"/>')


def stamp_svg():
    cx, cy = 64, 74
    circles = ''.join(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}"/>' for r in [2 + i * 1.9 for i in range(60)])
    # the gallery: a long roofed hall with a row of columns, a porch in the middle
    gallery = (f'<path d="M6 113 L10 109.5 H110 L114 113Z" fill="{RED}"/>'
               f'<rect x="6" y="113" width="108" height="11" fill="{RED}"/>'
               + ''.join(f'<rect x="{x:.1f}" y="115.6" width="1.5" height="6.4" fill="{PAPER}"/>' for x in [i * 3.3 + 9 for i in range(32)] if not 49 < x < 70)
               + f'<path d="M50 124 V106 L60 101 L70 106 V124Z" fill="{RED}"/>'
               + f'<path d="M56.6 124 V114.5 Q60 110.6 63.4 114.5 V124Z" fill="{PAPER}"/>'
               + f'<path d="M51.5 108.4 H68.5 M52.5 111 H67.5" stroke="{PAPER}" stroke-width=".45"/>')
    terrace = (f'<rect x="2" y="124" width="116" height="5.4" fill="{RED}"/>'
               f'<path d="M3 126.6 H117" stroke="{PAPER}" stroke-width=".5"/>'
               f'<path d="M53 129.4 L50 134 H70 L67 129.4Z" fill="{RED}"/>'
               f'<path d="M51.4 131 H68.6 M50.8 132.6 H69.2" stroke="{PAPER}" stroke-width=".45"/>')
    # the reflection in the moat: broken red strokes, fading
    ref = ''.join(f'<path d="M{rnd.uniform(4, 60):.1f} {y:.1f} h{rnd.uniform(8, 30):.1f} M{rnd.uniform(62, 104):.1f} {y + .6:.1f} h{rnd.uniform(6, 22):.1f}" '
                  f'stroke="{RED}" stroke-width=".9" opacity="{.55 - i * .08:.2f}" stroke-linecap="round"/>'
                  for i, y in enumerate([137.5, 140, 142.5, 145, 147.5]))
    towers = (tower(24, 112, 12, 24) + tower(96, 112, 12, 24)        # outer towers
              + tower(41, 112, 10.5, 20) + tower(79, 112, 10.5, 20)  # inner towers, a little behind
              + f'<path d="M46 113 V109.4 H48.6 V106.6 H51.4 V104 H68.6 V106.6 H71.4 V109.4 H74 V113Z" fill="{RED}"/>'
              + f'<path d="M48.6 109.4 H71.4 M51.4 106.6 H68.6" stroke="{PAPER}" stroke-width=".45"/>'
              + tower(60, 100, 15, 33))                               # the central tower, tallest, on its stepped base
    # a worn, printed look: specks of paper showing through the red
    specks = ''.join(f'<circle cx="{rnd.uniform(4, 116):.1f}" cy="{rnd.uniform(78, 134):.1f}" r="{rnd.uniform(.2, .55):.2f}"/>' for _ in range(90))
    birds = ''.join(bird(*b) for b in [(70, 41, .75, -10), (86, 31, 1.25, 8), (99, 20, .6, -16), (104, 42, .7, 14), (34, 54, .85, -6),
                                       (47, 63, .6, 12), (103, 62, .55, -12), (19, 70, .7, 10), (62, 46, .5, 2), (110, 80, .6, 16),
                                       (78, 50, .45, -4), (27, 84, .5, -12)])
    return f'''<svg class="env-stamp-in" viewBox="0 0 {W} {H}" role="img" aria-label="Stamp: Angkor Wat, Cambodia">
              <rect width="{W}" height="{H}" fill="{PAPER}"/>
              <g fill="none" stroke="#CFC9BF" stroke-width=".32">{circles}</g>
              <text x="11" y="24" class="stamp-name">CAMBODIA</text>
              <text x="11.4" y="34" class="stamp-khmer" fill="{RED}">កម្ពុជា</text>
              <text transform="translate(6.6 106) rotate(-90)" class="stamp-side">KINGDOM OF CAMBODIA</text>
              {birds}
              {towers}{gallery}{terrace}
              <g fill="{PAPER}" opacity=".75">{specks}</g>
              {ref}
            </svg>'''


if __name__ == '__main__':
    svg = stamp_svg()
    if '--write' not in sys.argv:
        print(svg)
        sys.exit()
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'pages', 'contact.html')
    s = open(p, encoding='utf-8').read()
    a = s.index('<svg class="env-stamp-in"')
    b = s.index('</svg>', a) + len('</svg>')
    s = s[:a] + svg + s[b:]
    open(p, 'w', encoding='utf-8').write(s)
    print('wrote the stamp into src/pages/contact.html')
