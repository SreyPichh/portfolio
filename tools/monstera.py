"""The monstera leaves used in the office drawing (tools/gen_room.py imports this).

Every leaf is heart-shaped: the stalk joins at the notch at (0, 0), two rounded lobes sit
either side of it, and in these coordinates the tip points up to (0, -156). In the room the
leaves are turned so they hang from their stalks, tip down and out, like a real plant.

Three kinds, so the plant doesn't look stamped out:
    mature   big leaf with curved slits cut in from the edge and a few holes
    split    a second mature leaf with a different slit pattern
    young    small plain heart, no slits
Each kind also bends a little to one side. Change the shapes here, then run
python3 tools/gen_room.py.
"""
import math

TIP = 156


def _bez(p0, p1, p2, p3, n=26):
    out = []
    for i in range(1, n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def _left_margin(width=1.0):
    """From the notch, round the left lobe, up the side, to the tip (width scales the leaf sideways)."""
    segs = [
        ((0, 0), (-3, 9), (-14, 21), (-31, 22)),
        ((-31, 22), (-52, 23), (-72, 8), (-79, -16)),
        ((-79, -16), (-87, -44), (-80, -80), (-63, -106)),
        ((-63, -106), (-46, -130), (-18, -147), (0, -TIP)),
    ]
    pts = [(0.0, 0.0)]
    for s in segs:
        pts += _bez(*s)
    return [(x * width, y) for x, y in pts]


def _acc(pts):
    acc = [0.0]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(x1 - x0, y1 - y0))
    return acc


def _at(pts, acc, s):
    for i in range(1, len(pts)):
        if acc[i] >= s:
            f = (s - acc[i - 1]) / max(acc[i] - acc[i - 1], 1e-9)
            return (pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f), i
    return pts[-1], len(pts) - 1


def _hit(pts, o, d):
    """Where the ray o + t*d first crosses the edge: (t, distance along the edge)."""
    acc, best = _acc(pts), None
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ex, ey = x1 - x0, y1 - y0
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-9:
            continue
        t = ((x0 - o[0]) * ey - (y0 - o[1]) * ex) / den
        u = ((x0 - o[0]) * d[1] - (y0 - o[1]) * d[0]) / den
        if t > 1 and 0 <= u <= 1 and (best is None or t < best[0]):
            best = (t, acc[i] + u * math.hypot(ex, ey))
    return best


def _dir(sign, ang):
    return (sign * math.cos(math.radians(ang)), -math.sin(math.radians(ang)))


def _curve(o, d, t0, t1, bow, n=10):
    """Points along a slit's centre line from t0 to t1 (fractions of the way out), bowing toward the tip."""
    out = []
    for k in range(n + 1):
        f = t0 + (t1 - t0) * k / n
        lift = bow * math.sin(math.pi * k / n)  # 0 at both ends, most in the middle
        out.append((o[0] + d[0] * f, o[1] + d[1] * f - lift))
    return out


def _cap(c, frm, to, outward, n=6):
    """Half-circle points around c, from frm to (not including) to, bulging toward outward."""
    a0 = math.atan2(frm[1] - c[1], frm[0] - c[0])
    r = math.hypot(frm[0] - c[0], frm[1] - c[1])
    for sgn in (1, -1):
        pts = [(c[0] + r * math.cos(a0 + sgn * math.pi * k / n), c[1] + r * math.sin(a0 + sgn * math.pi * k / n)) for k in range(1, n)]
        mid = pts[len(pts) // 2]
        if (mid[0] - c[0]) * outward[0] + (mid[1] - c[1]) * outward[1] > 0:
            return pts
    return pts


def _walls(centre, hw, taper=True):
    """The two sides of a slit that follows centre (offset half-width hw either side)."""
    left, right = [], []
    for i, (x, y) in enumerate(centre):
        a = centre[max(i - 1, 0)]
        b = centre[min(i + 1, len(centre) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, ty) or 1
        nx, ny = -ty / ln, tx / ln
        w = hw * (1.4 - .55 * i / (len(centre) - 1)) if taper else hw  # opens wider at the edge
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left, right


def _proj(pts, acc, p):
    """Distance along the edge of the edge point nearest p."""
    best = (1e18, 0.0)
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ex, ey = x1 - x0, y1 - y0
        L2 = ex * ex + ey * ey or 1e-9
        u = max(0.0, min(1.0, ((p[0] - x0) * ex + (p[1] - y0) * ey) / L2))
        qx, qy = x0 + ex * u, y0 + ey * u
        dd = (p[0] - qx) ** 2 + (p[1] - qy) ** 2
        if dd < best[0]:
            best = (dd, acc[i] + u * math.sqrt(L2))
    return best[1]


def _side(sign, spec, width):
    base = _left_margin(width)
    if sign > 0:
        base = [(-x, y) for x, y in base]
    acc = _acc(base)
    cuts, holes, veins = [], [], []
    for oy, ang, inner, hw in spec.get('slits', []):
        o, d = (0.0, oy), _dir(sign, ang)
        t, _ = _hit(base, o, d)
        centre = _curve(o, (d[0] * t, d[1] * t), 1.04, inner, bow=-t * .07)  # from just past the edge inward, curving like the veins
        left, right = _walls(centre, hw)
        inward = (centre[-1][0] - centre[-2][0], centre[-1][1] - centre[-2][1])
        sl, sr = _proj(base, acc, left[0]), _proj(base, acc, right[0])
        if sl <= sr:
            poly = left + _cap(centre[-1], left[-1], right[-1], inward) + right[::-1]
        else:
            poly = right + _cap(centre[-1], right[-1], left[-1], inward) + left[::-1]
        cuts.append((min(sl, sr), max(sl, sr), poly))
    for oy, ang, f0, f1, hw in spec.get('holes', []):
        o, d = (0.0, oy), _dir(sign, ang)
        t, _ = _hit(base, o, d)
        centre = _curve(o, (d[0] * t, d[1] * t), f0, f1, bow=-t * .02, n=6)
        left, right = _walls(centre, hw, taper=False)
        out_dir = (centre[0][0] - centre[1][0], centre[0][1] - centre[1][1])
        in_dir = (centre[-1][0] - centre[-2][0], centre[-1][1] - centre[-2][1])
        holes.append(left + _cap(centre[-1], left[-1], right[-1], in_dir) + right[::-1] + _cap(centre[0], right[0], left[0], out_dir))
    for oy, ang in spec.get('veins', []):
        o, d = (0.0, oy), _dir(sign, ang)
        t, _ = _hit(base, o, d)
        m = (o[0] + d[0] * t * .45, o[1] + d[1] * t * .45 - t * .06)
        e = (o[0] + d[0] * t * .84, o[1] + d[1] * t * .84 - t * .02)
        veins.append(((sign * 2.5, oy), m, e))
    cuts.sort()
    out, i = [], 0
    for s0, s1, poly in cuts:
        _, ia = _at(base, acc, s0)
        _, ib = _at(base, acc, s1)
        out += base[i:ia] + poly
        i = ib
    out += base[i:]
    return out, holes, veins


KINDS = {
    'mature': dict(width=1.0, bend=.10, left=dict(
        slits=[(-30, 14, .46, 3.6), (-56, 26, .4, 3.8), (-84, 36, .42, 3.6), (-110, 47, .5, 3.2)],
        holes=[(-12, -4, .5, .78, 2.6)],
        veins=[(-6, -20), (-18, 4), (-44, 20), (-70, 31), (-97, 41), (-122, 54)]),
        right=dict(
        slits=[(-26, 15, .5, 3.6), (-52, 27, .38, 3.8), (-80, 37, .44, 3.6), (-106, 48, .52, 3.2)],
        holes=[(-8, -2, .48, .76, 2.6)],
        veins=[(-4, -18), (-14, 5), (-40, 21), (-66, 32), (-93, 42), (-120, 55)])),
    'split': dict(width=.94, bend=-.12, left=dict(
        slits=[(-22, 10, .4, 3.8), (-50, 24, .34, 4.0), (-80, 35, .4, 3.6), (-108, 46, .5, 3.2)],
        holes=[],
        veins=[(-6, -16), (-36, 16), (-64, 29), (-94, 40), (-122, 54)]),
        right=dict(
        slits=[(-34, 18, .44, 3.8), (-64, 30, .36, 3.8), (-94, 41, .46, 3.4)],
        holes=[(-12, 0, .46, .74, 2.4)],
        veins=[(-4, -14), (-20, 8), (-50, 24), (-80, 35), (-108, 46)])),
    'young': dict(width=.86, bend=.08, left=dict(
        veins=[(-10, -6), (-40, 18), (-74, 32), (-108, 46)]),
        right=dict(
        veins=[(-8, -4), (-38, 19), (-72, 33), (-106, 47)])),
}


def leaf(kind='mature'):
    """Path data for one kind of leaf: (whole leaf, its shaded right half, midrib, side veins)."""
    k = KINDS[kind]
    left, lh, lv = _side(-1, k['left'], k['width'])
    right, rh, rv = _side(1, k['right'], k['width'])
    bend = k['bend']
    warp = lambda p: (p[0] + bend * TIP * (-p[1] / TIP) ** 2, p[1])  # bow the whole leaf a little to one side
    fmt = lambda pts: 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in map(warp, pts)) + 'Z'
    outline = left + right[::-1][1:]
    whole = fmt(outline) + ' ' + ' '.join(fmt(h) for h in lh + rh)
    rib_back = [(0.0, -TIP + TIP * i / 24) for i in range(1, 24)]
    shade = fmt(right + rib_back) + ' ' + ' '.join(fmt(h) for h in rh)
    rib = [warp((0, 2)), warp((0, -50)), warp((0, -100)), warp((0, -TIP + 8))]
    midrib = 'M{:.1f} {:.1f} C{:.1f} {:.1f} {:.1f} {:.1f} {:.1f} {:.1f}'.format(*[c for p in rib for c in p])
    sides = ' '.join('M{:.1f} {:.1f} Q{:.1f} {:.1f} {:.1f} {:.1f}'.format(*[c for p in map(warp, v) for c in p]) for v in lv + rv)
    return whole, shade, midrib, sides
