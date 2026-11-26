"""Builds the home-office SVG scene (one-point perspective, cel-shaded, no outlines)
and splices it into src/pages/index.html between <svg class="room" ...> and </svg>.

Usage (from the project folder):
    python3 tools/gen_room.py              # rebuilds src/pages/index.html (then run tools/build.py)
    python3 tools/gen_room.py path/to.html # or another file

Edit the drawing here, then run it; don't hand-edit the room inside src/pages/index.html,
because the next run replaces it. Wall colours, animations and the panels that
open from each object live in styles.css and script.js.
"""
import os, re, sys

EX, EY = 600, 470          # eye point (vanishing point)
out = []
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monstera import leaf as _monstera_leaf, KINDS as _MKINDS
def _monstera_defs():
    """One outline, shaded half and vein set per leaf kind: #mleaf-mature, #mshade-mature, #mveins-mature..."""
    out = []
    for k in _MKINDS:
        whole, shade, rib, sides = _monstera_leaf(k)
        out.append(f'<path id="mleaf-{k}" fill-rule="evenodd" d="{whole}"/>')
        out.append(f'<path id="mshade-{k}" fill-rule="evenodd" d="{shade}"/>')
        out.append(f'<g id="mveins-{k}" fill="none" stroke-linecap="round"><path d="{rib}" stroke="#C8EBA0" stroke-width="2.6" stroke-opacity=".85"/>'
                   f'<path d="{sides}" stroke="#C8EBA0" stroke-width="1.3" stroke-opacity=".5"/></g>')
    return '\n          '.join(out)
def w(s): out.append(s.replace('@@WINDOWVIEW@@', '              ' + window_view()) if '@@WINDOWVIEW@@' in s else s)

def lerp(a, b, k): return a + (b - a) * k
def back(x, y, k):          # point pushed back in depth toward the vanishing point
    return (round(lerp(x, EX, k), 1), round(lerp(y, EY, k), 1))
def poly(pts, fill, extra=''):
    d = 'M' + ' L'.join(f'{x} {y}' for x, y in pts) + 'Z'
    return f'<path d="{d}" fill="{fill}"{extra}/>'
def mirror(d, axis=780):
    return re.sub(r'(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)', lambda m: f'{round(2*axis-float(m.group(1)),1)} {m.group(2)}', d)

# ------------------------------------------------------------------ defs
def lg(id, stops, x2=0, y2=1, x1=0, y1=0):
    st = ''
    for o, c, a in stops:
        st += '<stop offset="%s" stop-color="%s"%s/>' % (o, c, '' if a is None else ' stop-opacity="%s"' % a)
    return '<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (id, x1, y1, x2, y2, st)
def S(*pairs):  # stops helper: (offset, color[, opacity])
    return [(p[0], p[1], p[2] if len(p) > 2 else None) for p in pairs]
V = dict(x2=0, y2=1); H = dict(x2=1, y2=0); D = dict(x2=1, y2=1)

defs = [
 '''<linearGradient id="gWin" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" style="stop-color:var(--sky-1)"/><stop offset=".55" style="stop-color:var(--sky-2)"/><stop offset="1" style="stop-color:var(--sky-3)"/>
          </linearGradient>
          <!-- the lake mirrors the sky: horizon colours at the far shore, deeper blue up close -->
          <linearGradient id="gLake" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" style="stop-color:var(--sky-3)"/><stop offset=".45" style="stop-color:var(--sky-2)"/><stop offset="1" style="stop-color:var(--sky-1)"/>
          </linearGradient>
          <!-- warm haze that sits on the horizon -->
          <linearGradient id="gHaze" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" style="stop-color:var(--glow)" stop-opacity="0"/><stop offset=".62" style="stop-color:var(--glow)" stop-opacity=".7"/><stop offset="1" style="stop-color:var(--glow)" stop-opacity="0"/>
          </linearGradient>
          <clipPath id="winFields"><path d="M560 368 C640 348 720 350 790 362 C850 372 920 358 1000 354 V440 H560Z"/></clipPath>
          <radialGradient id="gSun" cx=".4" cy=".35" r=".7">
            <stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" style="stop-color:var(--sun)"/><stop offset="1" style="stop-color:var(--sun-edge)"/>
          </radialGradient>
          <radialGradient id="gHalo"><stop offset="0" style="stop-color:var(--glow)" stop-opacity=".9"/><stop offset="1" style="stop-color:var(--glow)" stop-opacity="0"/></radialGradient>
          <mask id="bite"><rect x="-40" y="-40" width="80" height="80" fill="#fff"/><circle cx="10" cy="-7" r="17" fill="#000" style="fill-opacity:var(--moon, 0)"/></mask>
          <clipPath id="glass"><rect x="632" y="122" width="296" height="286"/></clipPath>
          <mask id="unlit" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="7200" height="7000">
            <rect x="-3000" y="-3000" width="7200" height="7000" fill="#fff"/>
            <rect x="632" y="122" width="296" height="286" fill="#000"/>
            <rect x="706" y="472" width="188" height="102" rx="3" fill="#000"/>
            <g class="lightholes">
              <ellipse cx="660" cy="590" rx="230" ry="160" fill="url(#gHole)"/>
              <ellipse cx="68" cy="430" rx="170" ry="250" fill="url(#gHole)"/>
              <ellipse cx="438" cy="300" rx="120" ry="100" fill="url(#gHole)"/>
            </g>
            <ellipse class="screenhole" cx="800" cy="590" rx="130" ry="95" fill="url(#gHole)"/>
          </mask>
          <radialGradient id="gLamp" cx=".5" cy=".45" r=".5">
            <stop offset="0" stop-color="#FFE4A8" stop-opacity=".78"/><stop offset=".22" stop-color="#FFDDA0" stop-opacity=".56"/><stop offset=".48" stop-color="#FFD898" stop-opacity=".28"/><stop offset=".75" stop-color="#FFD898" stop-opacity=".09"/><stop offset="1" stop-color="#FFD898" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="gLampAmbient" cx=".5" cy=".3" r=".5">
            <stop offset="0" stop-color="#FFE1A4" stop-opacity=".7"/><stop offset=".2" stop-color="#FFDB9C" stop-opacity=".5"/><stop offset=".45" stop-color="#FFD594" stop-opacity=".25"/><stop offset=".72" stop-color="#FFD08C" stop-opacity=".08"/><stop offset="1" stop-color="#FFD08C" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="gHole"><stop offset="0" stop-color="#000" stop-opacity=".9"/><stop offset=".3" stop-color="#000" stop-opacity=".72"/><stop offset=".6" stop-color="#000" stop-opacity=".35"/><stop offset=".85" stop-color="#000" stop-opacity=".08"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
          <radialGradient id="gWarmPool"><stop offset="0" stop-color="#FFD7A0" stop-opacity=".75"/><stop offset=".45" stop-color="#FFDDB0" stop-opacity=".4"/><stop offset="1" stop-color="#FFE3BC" stop-opacity="0"/></radialGradient>
          <radialGradient id="gLampPool"><stop offset="0" stop-color="#FFF0C8" stop-opacity="1"/><stop offset=".5" stop-color="#FFE3A8" stop-opacity=".48"/><stop offset="1" stop-color="#FFE3A8" stop-opacity="0"/></radialGradient>
          <filter id="lampBlur" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="9"/></filter>
          <linearGradient id="gCone" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#FFF1C4" stop-opacity=".55"/><stop offset=".6" stop-color="#FFEBB8" stop-opacity=".18"/><stop offset="1" stop-color="#FFEBB8" stop-opacity="0"/>
          </linearGradient>
          <linearGradient id="gBeam" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" style="stop-color:var(--sun)" stop-opacity=".55"/><stop offset="1" style="stop-color:var(--sun)" stop-opacity="0"/>
          </linearGradient>
          <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="8"/></filter>
          <filter id="etch" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy=".35" stdDeviation=".25" flood-color="#6F8799" flood-opacity=".85"/></filter>
          <filter id="figGlow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur in="SourceAlpha" stdDeviation="3.2" result="b"/><feFlood flood-color="#C6FF7A"/><feComposite in2="b" operator="in"/></filter>
          <filter id="etchHalo" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="1.4"/></filter>
          <filter id="whiteSil" x="0" y="0" width="100%" height="100%"><feFlood flood-color="#fff"/><feComposite in2="SourceAlpha" operator="in"/></filter>
          <filter id="outline" x="-25%" y="-25%" width="160%" height="160%" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="7" dy="6" result="sb"/>
            <feFlood flood-color="#5B4630" flood-opacity=".24"/><feComposite in2="sb" operator="in" result="sh"/>
            <feMorphology in="SourceAlpha" operator="dilate" radius="2.4" result="d"/>
            <feFlood style="flood-color:var(--accent)" result="c"/><feComposite in="c" in2="d" operator="in" result="o"/>
            <feMerge><feMergeNode in="sh"/><feMergeNode in="o"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="cast" x="-25%" y="-20%" width="165%" height="150%" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceAlpha" stdDeviation="2.5"/><feOffset dx="18" dy="3" result="o"/>
            <feFlood style="flood-color:var(--wall-shadow)" flood-opacity=".42"/><feComposite in2="o" operator="in" result="s"/>
            <feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="cast-sm" x="-30%" y="-30%" width="170%" height="170%" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceAlpha" stdDeviation="1.2"/><feOffset dx="5" dy="3" result="o"/>
            <feFlood flood-color="#1A1A30" flood-opacity=".34"/><feComposite in2="o" operator="in" result="s"/>
            <feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="cast-plant" x="-30%" y="-30%" width="190%" height="170%" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceAlpha" stdDeviation="2"/><feOffset dx="40" dy="14" result="o"/>
            <feFlood style="flood-color:var(--wall-shadow)" flood-opacity=".38"/><feComposite in2="o" operator="in" result="s"/>
            <feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <radialGradient id="gSpill"><stop offset="0" stop-color="#FFFDF6" stop-opacity=".6"/><stop offset="1" stop-color="#FFFDF6" stop-opacity="0"/></radialGradient>
          <radialGradient id="gRug" cx=".5" cy=".45" r=".55"><stop offset="0" stop-color="#EEF1FA"/><stop offset=".8" stop-color="#DCE3F4"/><stop offset="1" stop-color="#C9D3EC"/></radialGradient>
                    <radialGradient id="gPearl" cx=".38" cy=".34" r=".66"><stop offset="0" stop-color="#A6D97E"/><stop offset=".56" stop-color="#A6D97E"/><stop offset=".56" stop-color="#6AAA4A"/><stop offset="1" stop-color="#6AAA4A"/></radialGradient>
          <radialGradient id="gFace" cx=".45" cy=".4" r=".65"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".85" stop-color="#F7F2E8"/><stop offset="1" stop-color="#E6DFD2"/></radialGradient>''',
 '<linearGradient id="gAOup" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--wall-shadow)" stop-opacity="0"/><stop offset="1" style="stop-color:var(--wall-shadow)" stop-opacity=".3"/></linearGradient>',
 lg('gAOdown', S((0,'#4A3A28',.3),(1,'#4A3A28',0))),
 lg('gAOr', S((0,'#4A3A28',.2),(1,'#4A3A28',0)), **H),
 lg('gAOl', S((0,'#4A3A28',0),(1,'#4A3A28',.2)), **H),
 lg('gShadeH', S((0,'#fff',.3),(.4,'#fff',0),(.7,'#000',0),(1,'#000',.16)), **H),
 lg('gShadeV', S((0,'#fff',.28),(.45,'#fff',0),(1,'#000',.14)), **V),
 lg('gWall', S((0,'#EDE4D4'),(.55,'#F4EDE1'),(1,'#F1E9DB')), **V),
 lg('gWains', S((0,'#ECE2D0'),(1,'#E5D9C4')), **V),
 lg('gFloor', S((0,'#D4B48B'),(.25,'#DDC19C'),(1,'#C9A579')), **V),
 lg('gBase', S((0,'#FFFDF8'),(1,'#EFE7D8')), **V),
 lg('gOakF', S((0,'#EFDDBC'),(1,'#D9BF96')), **D),
 lg('gOakSide', S((0,'#C9AB81'),(1,'#B89A70')), **H),
 lg('gOakEdge', S((0,'#F5E7CC'),(1,'#DCC39B')), **V),
 lg('gOakTop', S((0,'#D3B990'),(1,'#E9D6B4')), **V),
 lg('gCBack', S((0,'#B09169'),(1,'#C6AA82')), **V),
 lg('gInL', S((0,'#A9895F'),(1,'#B5976E')), **H),
 lg('gInR', S((0,'#D3B990'),(1,'#C8AC84')), **H),
 lg('gInTop', S((0,'#A08259'),(1,'#AE9168')), **V),
 lg('gFrameW', S((0,'#FFFFFF'),(1,'#E9E2D5')), **D),
 lg('gBrass', S((0,'#F7E3A0'),(.5,'#E3BE62'),(1,'#B98F3B')), **V),
 lg('gGold', S((0,'#B98A33'),(.3,'#F7E09A'),(.55,'#E8C25E'),(1,'#B08029')), **H),
 lg('gAlu', S((0,'#CBC8C1'),(.45,'#F4F3EF'),(1,'#C4C0B8')), **H),
 lg('gBezel', S((0,'#FBFAF6'),(1,'#E6E2DA')), **V),
 lg('gTerra', S((0,'#F0B08A'),(.45,'#DE8C64'),(1,'#BE6C49')), **H),
 lg('gCeramic', S((0,'#FFFFFF'),(.5,'#F3EFE7'),(1,'#D9D2C4')), **H),
 lg('gLilac', S((0,'#E3DDFA'),(1,'#B7ACE6')), **H),
 lg('gMug', S((0,'#FAD2DC'),(.5,'#F1AFC1'),(1,'#DA8DA3')), **H),
 lg('gLeaf', S((0,'#86B873'),(1,'#4A7C43')), **V),
 lg('gLeafB', S((0,'#9CC888'),(1,'#5D9151')), **V),
 lg('gLeafC', S((0,'#73A563'),(1,'#3F6E3B')), **V),
 lg('gCurtain', S((0,'#F6E3E9'),(.14,'#E7C8D2'),(.3,'#F7E6EB'),(.46,'#E4C3CE'),(.62,'#F5E2E8'),(.8,'#E6C7D1'),(1,'#F0D8E0')), **H),
 lg('gDeskTop', S((0,'#D9C19A'),(1,'#EEDCBD')), **V),
 lg('gDeskEdge', S((0,'#F0E0C3'),(1,'#D5BB92')), **V),
 lg('gLeg', S((0,'#E3CCA6'),(1,'#C4A57C')), **H),
 lg('gCab', S((0,'#FBF7EF'),(1,'#EAE2D3')), **V),
 lg('gCabSide', S((0,'#D9CFBD'),(1,'#CBC0AC')), **H),
 lg('gBasket', S((0,'#E2C597'),(1,'#C6A270')), **V),
 lg('gShade', S((0,'#F9E39D'),(.6,'#EEC765'),(1,'#D9AA45')), **D),
 lg('gClockRim', S((0,'#6A83DC'),(1,'#2E46A2')), **D),
 lg('gChairBack', S((0,'#BFD6B1'),(1,'#8FAF81')), **V),
 lg('gChairSeat', S((0,'#B2CBA3'),(1,'#86A678')), **V),
 lg('gMetal', S((0,'#7A7F8B'),(.5,'#5C616C'),(1,'#454A54')), **H),
 lg('gSoil', S((0,'#5C4230'),(1,'#7A5A42')), **V),
 lg('gNeck', S((0,'#8F5E3C'),(1,'#6B432A')), **H),
 lg('gPaper', S((0,'#FFFEFA'),(1,'#EFE8DA')), **V),
 lg('gRecord', S((0,'#F7F2E8'),(1,'#E3DACA')), **V),
 lg('gVinyl', S((0,'#454A57'),(1,'#22252D')), **V),
]
defs.append('''
          <filter id="edge1" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.4"/></filter>
          <filter id="edge6" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>
          <clipPath id="paneClip">
            <rect width="134" height="176" rx="2" transform="matrix(1 .2 -.34 1 1000 54)"/><rect x="146" width="134" height="176" rx="2" transform="matrix(1 .2 -.34 1 1000 54)"/>
            <rect y="188" width="134" height="176" rx="2" transform="matrix(1 .2 -.34 1 1000 54)"/><rect x="146" y="188" width="134" height="176" rx="2" transform="matrix(1 .2 -.34 1 1000 54)"/>
          </clipPath>
          <g id="panes">
            <g transform="matrix(1 .2 -.34 1 1000 54)">
              <rect width="134" height="176" rx="2"/><rect x="146" width="134" height="176" rx="2"/>
              <rect y="188" width="134" height="176" rx="2"/><rect x="146" y="188" width="134" height="176" rx="2"/>
            </g>
          </g>
          <g id="dapple">
            <g class="dap" style="--o:900px 60px">
              <path d="M860 40 C930 70 990 120 1040 200 M940 90 C960 120 1000 150 1030 160 M990 150 C1010 190 1050 220 1090 236" style="stroke:var(--wall-2)" stroke-width="5" fill="none"/>
              <use href="#mleaf" transform="translate(1010 150) rotate(120) scale(.55)" style="fill:var(--wall-2)"/>
              <use href="#mleaf" transform="translate(1044 210) rotate(70) scale(.5)" style="fill:var(--wall-2)"/>
              <use href="#mleaf" transform="translate(960 108) rotate(160) scale(.45)" style="fill:var(--wall-2)"/>
              <use href="#mleaf" transform="translate(1090 236) rotate(100) scale(.42)" style="fill:var(--wall-2)"/>
              <use href="#hleaf" transform="translate(1032 162) rotate(-40) scale(2.2)" style="fill:var(--wall-2)"/>
              <use href="#hleaf" transform="translate(1000 196) rotate(-110) scale(2)" style="fill:var(--wall-2)"/>
            </g>
            <g class="dap d2" style="--o:1300px 300px">
              <use href="#mleaf" transform="translate(1240 360) rotate(-120) scale(.5)" style="fill:var(--wall-2)"/>
              <use href="#mleaf" transform="translate(1200 410) rotate(-80) scale(.42)" style="fill:var(--wall-2)"/>
              <path d="M1300 300 C1270 330 1250 360 1240 360 M1270 340 C1240 380 1220 400 1200 410" style="stroke:var(--wall-2)" stroke-width="4" fill="none"/>
            </g>
          </g>
          <mask id="sunMask" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="7200" height="7000">
            <use href="#panes" fill="#fff" filter="url(#edge6)"/>
          </mask>
          <mask id="sunCore" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="7200" height="7000">
            <use href="#panes" fill="#fff" filter="url(#edge1)"/>
          </mask>
          <pattern id="brush" width="260" height="260" patternUnits="userSpaceOnUse">
            <rect width="260" height="260" filter="url(#brushF)"/>
          </pattern>
          <filter id="brushF" x="0" y="0" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency=".011 .09" numOctaves="3" seed="5" stitchTiles="stitch"/>
            <feColorMatrix values="1 0 0 0 0  1 0 0 0 0  1 0 0 0 0  0 0 0 0 1"/>
          </filter>
          <!-- monstera leaves (drawn by tools/monstera.py): heart-shaped, the stalk joins at the notch at 0,0 and the tip points up -->
          @@MONSTERA@@
          <g id="pleaf">
            <path d="M0 0 C-12 1 -19 -9 -18 -21 C-17 -33 -9 -42 2 -51 C11 -42 18 -33 18 -21 C19 -9 12 1 0 0Z"/>
            <path d="M-3 -6 C-7 -18 -7 -30 -2 -42 M5 -10 C8 -20 8 -28 5 -38 M-9 -14 C-11 -20 -10 -26 -8 -30" stroke="#E4F29C" stroke-width="2.4" stroke-linecap="round" fill="none" opacity=".55"/>
            <path d="M0 -2 C0 -18 0 -34 2 -49" stroke="#C6E894" stroke-width="1.1" fill="none" opacity=".8"/>
            <ellipse cx="-8" cy="-28" rx="3" ry="8" transform="rotate(20 -8 -28)" fill="#fff" opacity=".28"/>
          </g>
          <pattern id="ginghamSm" width="6" height="6" patternUnits="userSpaceOnUse">
            <rect width="6" height="6" fill="#F6EFDF"/><rect width="3" height="6" fill="#86A8C8" opacity=".55"/><rect width="6" height="3" fill="#86A8C8" opacity=".55"/>
          </pattern>
          <linearGradient id="gArtGreen" x1="0" y1="0" x2=".4" y2="1"><stop offset="0" stop-color="#E3F0D6"/><stop offset="1" stop-color="#B9D3A8"/></linearGradient>
          <linearGradient id="gArtBlue" x1="0" y1="0" x2=".4" y2="1"><stop offset="0" stop-color="#E4ECFA"/><stop offset="1" stop-color="#B9CCF1"/></linearGradient>
          <linearGradient id="gArtSun" x1="0" y1="0" x2=".4" y2="1"><stop offset="0" stop-color="#FCF3D6"/><stop offset="1" stop-color="#F3DC94"/></linearGradient>
          <pattern id="airmailSm" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="6" height="6" fill="#FBF8F1"/><rect width="1.8" height="6" fill="#C8463A"/><rect x="3" width="1.8" height="6" fill="#3F5DAE"/>
          </pattern>
          <linearGradient id="gPhoneScreen" x1="0" y1="0" x2=".5" y2="1"><stop offset="0" stop-color="#E9E3F7"/><stop offset=".55" stop-color="#DCE7F8"/><stop offset="1" stop-color="#F6E1E8"/></linearGradient>
          <!-- pages darken softly toward the spine -->
          <linearGradient id="gGutterL" x1="0" y1="0" x2="1" y2="0"><stop offset=".6" stop-color="#5A4A30" stop-opacity="0"/><stop offset="1" stop-color="#5A4A30" stop-opacity=".16"/></linearGradient>
          <linearGradient id="gGutterR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5A4A30" stop-opacity=".18"/><stop offset=".4" stop-color="#5A4A30" stop-opacity="0"/></linearGradient>
          <linearGradient id="gCylLight" x1="0" y1="0" x2="1" y2="0">
            <stop offset=".1" stop-color="#FFF6DE" stop-opacity="0"/><stop offset=".22" stop-color="#FFF6DE" stop-opacity=".32"/><stop offset=".36" stop-color="#FFF6DE" stop-opacity="0"/>
          </linearGradient>
          <linearGradient id="gCylShade" x1="0" y1="0" x2="1" y2="0">
            <stop offset=".55" stop-color="#3A2410" stop-opacity="0"/><stop offset="1" stop-color="#3A2410" stop-opacity=".22"/>
          </linearGradient>
          <pattern id="gingham" width="12" height="12" patternUnits="userSpaceOnUse">
            <rect width="12" height="12" fill="#F6EFDF"/><rect width="6" height="12" fill="#86A8C8" opacity=".55"/><rect width="12" height="6" fill="#86A8C8" opacity=".55"/>
          </pattern>
          <pattern id="grille" width="4" height="4" patternUnits="userSpaceOnUse">
            <rect width="4" height="4" fill="#8E5A36"/><rect width="2" height="2" fill="#C88A55"/><rect x="2" y="2" width="2" height="2" fill="#B57744"/>
          </pattern>
          <pattern id="boucle" width="7" height="5" patternUnits="userSpaceOnUse">
            <circle cx="1.6" cy="1.4" r=".9" fill="#E2D6C2" opacity=".7"/><circle cx="5.2" cy="3.8" r=".9" fill="#E2D6C2" opacity=".7"/>
            <circle cx="4.6" cy="1" r=".6" fill="#FFFCF5" opacity=".8"/><circle cx="1.2" cy="3.6" r=".6" fill="#FFFCF5" opacity=".8"/>
          </pattern>
          <pattern id="weavefine" width="3" height="2" patternUnits="userSpaceOnUse">
            <rect width="3" height="1" fill="#FFFFFF" opacity=".25"/><rect y="1" width="1.5" height="1" fill="#8C7E6A" opacity=".12"/>
          </pattern>
          <path id="hleaf" d="M0 0 C-7 -4 -15 1 -15 10 C-15 18 -7 23 0 29 C7 23 15 18 15 10 C15 1 7 -4 0 0Z"/>
          <pattern id="weave" width="10" height="8" patternUnits="userSpaceOnUse">
            <path d="M0 4 H10" stroke="#A8844F" stroke-width="1" opacity=".45"/><path d="M5 0 V4 M0 4 V8" stroke="#A8844F" stroke-width="1" opacity=".35"/>
          </pattern>''')

# ------------------------------------------------------------------ shell
w('''<!-- ===== Wall + floor ===== -->
        <g class="shell">
          <rect x="-3000" y="-3000" width="7200" height="3772" fill="url(#gWall)"/>
          <rect x="-3000" y="556" width="7200" height="200" fill="url(#gWains)"/>''')
grooves = ' '.join(f'M{x} 568 V748 M{x + 4} 568 V748' for x in range(-300, 1500, 36))
lights = ' '.join(f'M{x + 1.8} 568 V748' for x in range(-300, 1500, 36))
w(f'''          <path d="{grooves}" style="stroke:var(--wall-shadow)" stroke-opacity=".3" stroke-width="1.3"/>
          <path d="{lights}" stroke="#FFFFFF" stroke-opacity=".16" stroke-width=".9"/>''')
beads = ' '.join(f'M{x} 566 V750' for x in range(-280, 1500, 30))
w(f'''          <rect x="-3000" y="550" width="7200" height="12" fill="url(#gBase)"/>
          <rect x="-3000" y="562" width="7200" height="5" fill="#CDBEA6" opacity=".45"/>
          <rect x="-3000" y="772" width="7200" height="2400" fill="url(#gFloor)"/>''')
planks = [790, 812, 840, 878, 930, 1000]
w('          <path d="' + ' '.join(f'M-3000 {y} H4200' for y in planks) + '" stroke="#9C8566" stroke-opacity=".22" stroke-width="1.2"/>')
seams = []
for i, (y0, y1) in enumerate(zip([772] + planks[:-1], planks)):
    for x in range(-200 + (i * 170) % 340, 1500, 340):
        seams.append(f'M{x} {y0} V{y1}')
w('          <path d="' + ' '.join(seams) + '" stroke="#9C8566" stroke-opacity=".2" stroke-width="1.1"/>')
w('''          <rect x="-3000" y="748" width="7200" height="26" fill="url(#gBase)"/>
          <rect x="-3000" y="748" width="7200" height="2" fill="#fff" opacity=".8"/>
        </g>
        <g pointer-events="none">
          <ellipse cx="780" cy="270" rx="420" ry="330" fill="url(#gSpill)" opacity=".28"/>
          <rect x="-3000" y="718" width="7200" height="30" fill="url(#gAOup)"/>
          <rect x="-3000" y="774" width="7200" height="40" fill="url(#gAOdown)"/>
        </g>
''')
def cubic(p0, p1, p2, p3, t):
    mt = 1 - t
    return (mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0],
            mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1])
# --- rug: a faded vintage Persian-style rug lying flat in floor perspective
import math as _m, random as _r
_rr = _r.Random(21)
RW, RD = 780, 360                                   # rug size in its own flat units
RB, RF = 786, 856                                   # screen y of the back and front edges
RXL = (420, 380); RXR = (1059, 1160)                # (back, front) x of the left and right edges
def rp(px, pz):
    """flat rug point -> screen point (pz 0 = back edge)"""
    v = pz / RD
    y = RB + (RF - RB) * v
    xl = RXL[0] + (RXL[1] - RXL[0]) * v; xr = RXR[0] + (RXR[1] - RXR[0]) * v
    return xl + (xr - xl) * px / RW, y
def rscale(pz):
    v = pz / RD
    return ((RXR[0] + (RXR[1] - RXR[0]) * v) - (RXL[0] + (RXL[1] - RXL[0]) * v)) / RW
def rpoly(pts):
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in (rp(*q) for q in pts)) + 'Z'
def rline(pts):
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in (rp(*q) for q in pts))
def rrect(inset):
    return rpoly([(inset, inset), (RW - inset, inset), (RW - inset, RD - inset), (inset, RD - inset)])
def rcurve(p0, p1, p2, p3, n=18):
    return rline([cubic(p0, p1, p2, p3, i / n) for i in range(n + 1)])
def rflower(px, pz, r, col):
    x, y = rp(px, pz); s = rscale(pz); sq = .32
    o = ''.join(f'<ellipse cx="{x + _m.cos(a) * r * s:.1f}" cy="{y + _m.sin(a) * r * s * sq:.1f}" rx="{r * s * .62:.1f}" ry="{r * s * .62 * sq:.1f}" fill="{col}"/>' for a in [k * _m.pi * 2 / 5 for k in range(5)])
    return o + f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * s * .45:.1f}" ry="{r * s * .45 * sq:.1f}" fill="#E9DCC6"/>'
def rleaf(px, pz, r, ang, col):
    x, y = rp(px, pz); s = rscale(pz)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * s:.1f}" ry="{r * s * .3:.1f}" transform="rotate({ang:.0f} {x:.1f} {y:.1f})" fill="{col}"/>'
ROSE, CORAL, SLATE, SAGE, VINE = '#C98C7C', '#D3A088', '#8C9AA0', '#A3A893', '#9E9282'

parts = []
# body, thickness and soft edge
parts.append(f'<ellipse cx="770" cy="862" rx="400" ry="12" fill="#4E3320" opacity=".16" filter="url(#soft)"/>')
fx0, fy0 = rp(0, RD); fx1, fy1 = rp(RW, RD)
parts.append(f'<path d="M{fx0:.1f} {fy0:.1f} L{fx1:.1f} {fy1:.1f} L{fx1 + .6:.1f} {fy1 + 3.2:.1f} L{fx0 - .6:.1f} {fy0 + 3.2:.1f}Z" fill="#BDAE96"/>')
parts.append(f'<path d="{rrect(0)}" fill="url(#gPersian)"/>')
# border: outer band + inner band lines
parts.append(f'<path d="{rrect(9)}" fill="none" stroke="#B8AA95" stroke-width="1.1"/>')
parts.append(f'<path d="{rrect(14)}" fill="none" stroke="#CFC2AE" stroke-width=".8"/>')
parts.append(f'<path d="{rrect(48)}" fill="none" stroke="#A89A86" stroke-width="1.2"/>')
parts.append(f'<path d="{rrect(53)}" fill="none" stroke="#C8BBA6" stroke-width=".8"/>')
# border motif: little flowers + leaf pairs running around the band (midway between 14 and 48)
band = 31
def edge_points():
    pts = []
    for x in range(int(band), int(RW - band), 26): pts.append((x, band)); pts.append((x + 13, RD - band))
    for z in range(int(band) + 20, int(RD - band), 26): pts.append((band, z)); pts.append((RW - band, z + 13))
    return pts
for i, (px, pz) in enumerate(edge_points()):
    parts.append(rleaf(px - 7, pz, 5, -25, SAGE if i % 2 else SLATE))
    parts.append(rleaf(px + 7, pz, 5, 25, SLATE if i % 2 else SAGE))
    parts.append(rflower(px, pz, 3.6, ROSE if i % 3 else CORAL))
# field: curling vines with leaves and rosettes
for _ in range(26):
    x0 = _rr.uniform(70, RW - 70); z0 = _rr.uniform(70, RD - 70)
    dx = _rr.uniform(-90, 90); dz = _rr.uniform(-60, 60)
    p0 = (x0, z0); p3 = (min(RW - 62, max(62, x0 + dx)), min(RD - 62, max(62, z0 + dz)))
    p1 = (x0 + _rr.uniform(-60, 60), z0 + _rr.uniform(-50, 50)); p2 = (p3[0] + _rr.uniform(-60, 60), p3[1] + _rr.uniform(-50, 50))
    clamp_ = lambda q: (min(RW - 60, max(60, q[0])), min(RD - 60, max(60, q[1])))
    p1, p2 = clamp_(p1), clamp_(p2)
    parts.append(f'<path d="{rcurve(p0, p1, p2, p3)}" fill="none" stroke="{VINE}" stroke-width=".9" opacity=".75"/>')
    for t in (.25, .5, .75):
        q = cubic(p0, p1, p2, p3, t)
        parts.append(rleaf(q[0] + 4, q[1], 4.6, _rr.uniform(-40, 40), _rr.choice([SAGE, SLATE, '#B3AA98'])))
    for t in (0, 1):
        q = (p0, p3)[t]
        parts.append(rflower(q[0], q[1], _rr.uniform(4, 6.4), _rr.choice([ROSE, CORAL, ROSE, '#B99B8E'])))
# soft wear: a few lighter patches, and a fine woven speckle
for _ in range(7):
    x, y = rp(_rr.uniform(80, RW - 80), _rr.uniform(60, RD - 60))
    parts.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{_rr.uniform(30, 70):.0f}" ry="{_rr.uniform(4, 9):.0f}" fill="#F3EDE2" opacity=".35" filter="url(#soft)"/>')
parts.append(f'<path d="{rrect(0)}" fill="url(#weavefine)" opacity=".55"/>')
# a light catch along the back edge
bx0, by0 = rp(0, 0); bx1, by1 = rp(RW, 0)
parts.append(f'<path d="M{bx0:.1f} {by0:.1f} L{bx1:.1f} {by1:.1f}" stroke="#FBF6EC" stroke-width="1.2" opacity=".8"/>')
w('        <!-- rug: faded vintage Persian-style, ivory ground, rose & slate florals -->\n        <g class="rug">' + ''.join(parts) + '</g>')


w('''        <!-- contact shadows on the floor -->
        <g pointer-events="none" fill="#4E3320">
          <path d="M136 798 H474 L490 773 H500 L484 808 H140Z" opacity=".3" filter="url(#edge1)"/>
          <path d="M472 803 L490 774 L548 777 L526 806Z" opacity=".12" filter="url(#edge1)"/>
          <ellipse cx="520" cy="793" rx="34" ry="5" opacity=".34" filter="url(#edge1)"/>
          <path d="M496 790 L548 792 L566 776 L520 774Z" opacity=".14" filter="url(#edge1)"/>
          <ellipse cx="584" cy="797" rx="9" ry="2.6" opacity=".35"/>
          <ellipse cx="588" cy="773" rx="6" ry="2" opacity=".25"/>
          <path d="M874 793 H1004 L1012 773 H1022 L1008 803 H878Z" opacity=".28" filter="url(#edge1)"/>
          <ellipse cx="654" cy="799" rx="26" ry="3.6" opacity=".3" filter="url(#edge1)"/>
          <ellipse cx="1122" cy="802" rx="54" ry="5.5" opacity=".36" filter="url(#edge1)"/>
          <path d="M1164 800 L1250 790 L1262 802 L1172 808Z" opacity=".12" filter="url(#edge1)"/>
        </g>''')
# ------------------------------------------------------------------ the view outside
def window_view():
    """The landscape through the window. Every colour comes from the time-of-day palette
    (CSS variables set by script.js), so dawn, day, golden hour and night all repaint it."""
    mix = lambda a, b, pa: f'color-mix(in srgb, {a} {pa}%, {b})'
    v = []
    # haze along the horizon, then clouds and birds
    v.append('<rect x="560" y="196" width="440" height="140" fill="url(#gHaze)"/>')
    v.append('<use class="wcloud w1" href="#cloud" x="560" y="140" width="120" height="54"/>')
    v.append('<use class="wcloud w2" href="#cloud" x="560" y="206" width="86" height="40"/>')
    v.append('<use class="wcloud w3" href="#cloud" x="560" y="170" width="64" height="30" opacity=".85"/>')
    bird = lambda x, y, k: f'<path d="M{x - 4 * k:.1f} {y:.1f} q{2 * k:.1f} {-2.4 * k:.1f} {4 * k:.1f} 0 q{2 * k:.1f} {-2.4 * k:.1f} {4 * k:.1f} 0"/>'
    v.append(f'<g class="win-birds" fill="none" stroke-linecap="round" stroke-linejoin="round" style="stroke:{mix("var(--tree-2)", "var(--sky-1)", 70)}" stroke-width="1.3">'
             + bird(690, 196, 1.1) + bird(704, 188, .9) + bird(716, 199, .75) + '</g>')

    # far mountains: pale with distance, snow on the two tallest peaks, the right-hand faces in shade
    ridge = [(560, 300), (598, 278), (622, 288), (664, 252), (694, 272), (722, 262), (760, 230), (802, 268), (830, 258), (872, 240), (912, 268), (946, 256), (1000, 282)]
    v.append(f'<path d="M{" L".join(f"{x} {y}" for x, y in ridge)} V336 H560Z" style="fill:{mix("var(--mount-1)", "var(--sky-2)", 62)}"/>')
    for i in range(1, len(ridge) - 1):
        (px, py), (rx, ry) = ridge[i], ridge[i + 1]
        if py < ridge[i - 1][1] and py < ry:  # a peak: shade its right face
            base_x = px + (rx - px) * .3
            v.append(f'<path d="M{px} {py} L{rx} {ry} L{base_x + (rx - px) * .45:.1f} 318 L{base_x:.1f} 318Z" fill="#26304E" opacity=".08"/>')
    for (px, py) in [(760, 230), (872, 240)]:
        i = ridge.index((px, py))
        l, r = ridge[i - 1], ridge[i + 1]

        def along(q, d):  # a point d units down the slope toward q
            dx, dy = q[0] - px, q[1] - py
            return px + dx * d / dy, py + d
        (lx, ly), (rx, ry) = along(l, 13), along(r, 12)
        v.append(f'<path d="M{px} {py} L{rx:.1f} {ry:.1f} L{px + 6:.1f} {py + 8:.1f} L{px + 2:.1f} {py + 14:.1f} L{px - 3:.1f} {py + 9:.1f} L{lx:.1f} {ly:.1f}Z" style="fill:var(--cloud)" opacity=".92"/>')
        v.append(f'<path d="M{px} {py} L{rx:.1f} {ry:.1f} L{px + 6:.1f} {py + 8:.1f} L{px + 2:.1f} {py + 14:.1f}Z" style="fill:var(--cloud-shade)" opacity=".9"/>')

    # nearer mountains
    v.append('<path d="M560 314 C584 304 606 294 636 298 L672 280 L704 294 L740 286 C768 292 792 302 820 298 L856 278 L890 292 L928 284 L1000 302 V340 H560Z" fill="url(#gMount)"/>')
    v.append('<path d="M672 280 L704 294 L700 318 L682 318Z M856 278 L890 292 L884 318 L866 318Z" fill="#26304E" opacity=".07"/>')

    # the lake, with ripples and a soft glint of light
    v.append('<path d="M560 318 C640 314 760 316 860 318 C920 319 960 316 1000 318 V350 H560Z" fill="url(#gLake)"/>')
    v.append('<path d="M560 318 C640 314 760 316 860 318 C920 319 960 316 1000 318" fill="none" style="stroke:var(--mount-2)" stroke-width="1.2" opacity=".8"/>')
    v.append('<ellipse cx="790" cy="327" rx="46" ry="2.2" style="fill:var(--glow)" opacity=".75"/>')
    ripples = [(712, 323, 18), (748, 330, 26), (806, 334, 22), (842, 326, 14), (872, 331, 20), (770, 337, 30), (906, 338, 16), (690, 334, 12)]
    v.append('<g stroke="#fff" stroke-linecap="round" stroke-width="1" opacity=".55">' + ''.join(f'<path d="M{x} {y} h{w}"/>' for x, y, w in ripples) + '</g>')

    # back hills framing the lake: a cottage on the left bank, cypresses on the right
    v.append('<path d="M560 316 C600 304 652 306 690 320 C722 332 762 344 822 346 C880 348 940 330 1000 322 V440 H560Z" fill="url(#gBack)"/>')
    for x, y, h in [(846, 346, 30), (858, 345, 40), (871, 344, 28), (883, 342, 36), (896, 340, 26)]:
        v.append(f'<use href="#cypress" x="{x - h * .14:.1f}" y="{y - h * .92:.1f}" width="{h * .28:.1f}" height="{h:.1f}"/>')
    # the cottage (its window glows at night)
    wall, roof = mix('#FFF7E8', 'var(--hb-1)', 58), mix('#D9785A', 'var(--hb-2)', 62)
    v.append('<g class="cottage">'
             f'<path d="M682 306 V297 H686 V303Z" style="fill:{mix("#B98E73", "var(--hb-2)", 60)}"/>'
             f'<rect x="660" y="306" width="26" height="15" style="fill:{wall}"/>'
             f'<path d="M656 307 L673 294 L690 307Z" style="fill:{roof}"/>'
             '<path d="M673 294 L690 307 L686 307 L673 297Z" fill="#000" opacity=".12"/>'
             f'<rect x="665" y="311" width="5" height="5" style="fill:{mix("#7E93A6", "var(--hb-2)", 55)}"/>'
             # dusk falls over the cottage; then its lit window shows through
             '<path d="M656 307 L673 294 L690 307 H686 V321 H660 V307Z" fill="#1C2246" style="opacity:calc(var(--dark, 0) * .55)"/>'
             '<rect x="665" y="311" width="5" height="5" fill="#FFD27A" style="opacity:var(--dark, 0)"/>'
             f'<rect x="676" y="312" width="5" height="9" style="fill:{mix("#8A6448", "var(--hb-2)", 60)}"/>'
             '<g class="smoke" style="fill:var(--cloud)"><circle cx="684" cy="292" r="2.2"/><circle cx="687" cy="286" r="2.8"/><circle cx="691" cy="279" r="3.4"/></g>'
             '</g>')

    # middle fields: soft stripes of crops and a golden patch, with a hedge of round trees
    v.append('<path d="M560 368 C640 348 720 350 790 362 C850 372 920 358 1000 354 V440 H560Z" fill="url(#gMid)"/>')
    v.append(f'<path d="M818 386 C858 374 928 366 1000 362 V394 C930 396 868 402 824 404 C814 398 812 391 818 386Z" clip-path="url(#winFields)" style="fill:{mix("#F1D58A", "var(--hm-1)", 45)}; opacity:calc(1 - var(--dark, 0) * .7)"/>')
    stripes = ''.join(f'<path d="M560 {372 + k * 9} C640 {352 + k * 9} 720 {354 + k * 9} 790 {366 + k * 9} C850 {376 + k * 9} 920 {362 + k * 9} 1000 {358 + k * 9}"/>' for k in range(1, 8))
    v.append(f'<g clip-path="url(#winFields)" fill="none" stroke="#fff" stroke-width="2" opacity=".14">{stripes}</g>')
    for x, y, r in [(726, 352, 6.5), (738, 353, 5), (748, 355, 6), (760, 357, 4.6)]:
        v.append(f'<circle cx="{x}" cy="{y}" r="{r}" style="fill:var(--tree)"/>'
                 f'<path d="M{x} {y - r} a{r} {r} 0 0 1 0 {2 * r} a{r * .7:.1f} {r} 0 0 0 0 {-2 * r}Z" style="fill:var(--tree-2)" opacity=".5"/>')

    # front meadow: a winding path, two round trees and scattered flowers
    v.append('<path d="M560 398 C640 382 720 382 800 392 C860 399 930 394 1000 390 V440 H560Z" fill="url(#gFront)"/>')
    v.append('<path d="M796 442 C792 426 828 418 812 406 C802 399 790 396 784 391 L789 390 C799 394 816 398 828 405 C852 420 822 428 838 442Z" style="fill:var(--path)" opacity=".95"/>')
    for x, y, r in [(700, 370, 15), (726, 381, 9.5)]:
        v.append(f'<path d="M{x} {y + r * .4:.1f} V{y + r * 1.35:.1f}" style="stroke:var(--tree-2)" stroke-width="{r * .22:.1f}" stroke-linecap="round"/>')
        v.append(f'<circle cx="{x}" cy="{y}" r="{r}" style="fill:var(--tree)"/>')
        v.append(f'<path d="M{x} {y - r} a{r} {r} 0 0 1 0 {2 * r} a{r * .78:.1f} {r} 0 0 0 0 {-2 * r}Z" style="fill:var(--tree-2)" opacity=".55"/>')
        v.append(f'<circle cx="{x - r * .38:.1f}" cy="{y - r * .38:.1f}" r="{r * .3:.1f}" fill="#fff" opacity=".14"/>')
    flowers = [(668, 404, 'petal'), (676, 410, 'butter'), (690, 406, 'daisy'), (744, 402, 'petal'), (756, 410, 'daisy'), (770, 404, 'butter'),
               (850, 404, 'lilac'), (862, 410, 'daisy'), (876, 402, 'petal'), (890, 408, 'butter'), (712, 414, 'lilac'), (900, 416, 'daisy')]
    v.append('<g>' + ''.join(f'<circle cx="{x}" cy="{y}" r="1.7" style="fill:{mix(f"var(--{c})", "var(--hf-2)", 75)}"/>' for x, y, c in flowers) + '</g>')
    return '\n              '.join(v)


# ------------------------------------------------------------------ window
w('''
        <!-- ===== Window ===== -->
        <g class="obj big" id="o-window" data-id="window" tabindex="0" role="button" aria-label="Window: a peek outside">
          <g clip-path="url(#glass)">
            <g class="view">
              <rect x="560" y="100" width="440" height="340" fill="url(#gWin)"/>
              <g class="win-stars" fill="#FFF8E0">
                <circle cx="660" cy="150" r="1.6"/><circle cx="702" cy="190" r="1.1"/><circle cx="748" cy="140" r="1.4"/><circle cx="812" cy="176" r="1.8"/>
                <circle cx="858" cy="138" r="1.2"/><circle cx="900" cy="196" r="1.5"/><circle cx="680" cy="236" r="1"/><circle cx="770" cy="222" r="1.2"/>
                <circle cx="880" cy="250" r="1"/><circle cx="640" cy="200" r="1.3"/><circle cx="836" cy="214" r="1"/><circle cx="916" cy="160" r="1.1"/>
              </g>
              <g id="win-sun" transform="translate(760 180)">
                <circle r="58" fill="url(#gHalo)"/>
                <circle r="19" fill="url(#gSun)" mask="url(#bite)"/>
              </g>
@@WINDOWVIEW@@
            </g>
            <path d="M652 122 H700 L640 236 H632 V160Z M716 122 H732 L656 266 H648Z" fill="#fff" opacity=".18"/>
            <rect x="632" y="122" width="296" height="12" fill="url(#gAOdown)"/>
            <rect x="632" y="122" width="10" height="286" fill="url(#gAOr)"/>
          </g>
          <path fill-rule="evenodd" d="M616 106 H944 V424 H616Z M632 122 V408 H928 V122Z" fill="url(#gFrameW)"/>
          <path d="M616 106 H944 L932 118 H628Z" fill="#fff"/>
          <path d="M944 106 V424 L932 412 V118Z" fill="#E4DCCD"/>
          <rect x="776" y="122" width="8" height="286" fill="url(#gFrameW)"/>
          <rect x="632" y="261" width="296" height="8" fill="url(#gFrameW)"/>
          <rect x="632" y="269" width="296" height="3" fill="#000" opacity=".06"/>
          <rect x="598" y="420" width="364" height="10" rx="2" fill="#FFFFFF"/>
          <rect x="598" y="430" width="364" height="8" rx="2" fill="#E6DED0"/>
        </g>''')

# curtains: blue-and-cream gingham panels on a dark wooden rod with rings
cl = 'M570 98 L654 98 C655 220 657 380 660 524 Q648 530 636 524 Q624 530 612 524 Q600 530 588 524 Q577 529 566 524 C567 380 569 220 570 98Z'
fold = 'M584 112 C585 250 584 400 588 522 M600 112 C601 250 602 400 600 524 M618 112 C619 250 621 400 624 522 M638 112 C639 250 642 400 646 524'
rings_l = [576, 592, 608, 624, 640, 650]
rings = rings_l + [1560 - x for x in rings_l]
w(f'''        <g class="c-lg">
          <g class="cur cur-l">
            <path d="{cl}" fill="url(#gingham)"/>
            <path d="{cl}" fill="url(#gPleat)"/>
            <path d="{fold}" stroke="#4E6F92" stroke-opacity=".18" stroke-width="1.4" fill="none"/>
            <path d="M570 98 L654 98 L654 108 Q612 112 570 108Z" fill="#000" opacity=".06"/>
          </g>
          <g class="cur cur-r">
            <path d="{mirror(cl)}" fill="url(#gingham)"/>
            <path d="{mirror(cl)}" fill="url(#gPleat)"/>
            <path d="{mirror(fold)}" stroke="#4E6F92" stroke-opacity=".18" stroke-width="1.4" fill="none"/>
            <path d="{mirror('M570 98 L654 98 L654 108 Q612 112 570 108Z')}" fill="#000" opacity=".06"/>
          </g>
          <rect x="548" y="87" width="464" height="7" rx="3.5" fill="url(#gDarkWood)"/>
          <rect x="548" y="87.6" width="464" height="1.4" rx=".7" fill="#A07A55" opacity=".7"/>
          <circle cx="545" cy="90.5" r="8" fill="url(#gDarkWood)"/><rect x="551" y="85" width="4" height="11" rx="1.5" fill="#4A3322"/>
          <circle cx="1015" cy="90.5" r="8" fill="url(#gDarkWood)"/><rect x="1005" y="85" width="4" height="11" rx="1.5" fill="#4A3322"/>
          <g fill="none" stroke="#4A3322" stroke-width="2.4">{''.join(f'<circle cx="{x}" cy="93" r="5.5"/>' for x in rings)}</g>
          <g fill="#F6EFDF">{''.join(f'<rect x="{x - 4}" y="97" width="8" height="5" rx="1"/>' for x in rings)}</g>
        </g>''')

# ------------------------------------------------------------------ wall decor
w('''
        <!-- Travel map postcard, taped to the wall -->
        <g class="obj" id="o-map" data-id="map" tabindex="0" role="button" aria-label="Map: where I've been">
          <g transform="translate(-14 0) rotate(-4 530 226)">
            <clipPath id="mapClip"><rect x="492" y="196" width="76" height="60" rx="1"/></clipPath>
            <rect x="486" y="190" width="88" height="72" rx="1.5" fill="#F7F0E1"/>
            <path d="M562 262 L574 252 L574 262Z" fill="#E6DCC6"/>
            <rect x="489" y="193" width="82" height="66" fill="none" stroke="#C9B48E" stroke-width=".6"/>
            <g clip-path="url(#mapClip)">
              <rect x="492" y="196" width="76" height="60" fill="url(#gSea)"/>
              <path d="M498 204 q2 -1.4 4 0 q2 1.4 4 0 M540 252 q2 -1.4 4 0 q2 1.4 4 0 M552 210 q2 -1.4 4 0 q2 1.4 4 0 M500 248 q2 -1.4 4 0 q2 1.4 4 0" stroke="#9FBDD6" stroke-width=".7" fill="none"/>
              <path d="M490 214 C498 206 508 210 514 205 C522 199 532 203 534 210 C537 218 528 222 530 229 C532 236 522 240 514 236 C506 232 500 238 494 234 C488 230 486 220 490 214Z" fill="#DDE5C3" stroke="#9FB384" stroke-width=".7"/>
              <path d="M540 228 C546 222 556 224 560 218 C566 212 574 216 574 224 L574 262 L548 262 C544 256 548 250 544 244 C540 238 536 234 540 228Z" fill="#E4DDBE" stroke="#A8A67E" stroke-width=".7"/>
              <path d="M548 196 C552 194 558 196 560 200 C562 204 556 206 552 204 C548 203 545 199 548 196Z" fill="#DDE5C3" stroke="#9FB384" stroke-width=".6"/>
              <path d="M500 218 C504 214 510 216 512 220 C508 222 504 223 500 218Z M518 226 C522 223 526 225 527 228 C523 230 520 230 518 226Z M552 236 C556 233 561 235 562 238 C558 240 555 240 552 236Z" fill="#C3D09E"/>
              <g fill="#7E9A66"><circle cx="506" cy="226" r="1.1"/><circle cx="509" cy="228" r="1"/><circle cx="524" cy="216" r="1.1"/><circle cx="560" cy="246" r="1"/><circle cx="563" cy="243" r="1.1"/></g>
              <path d="M504 230 C514 214 528 210 540 216 C548 220 552 230 558 232" stroke="#C8443C" stroke-width="1" fill="none" stroke-dasharray="2.2 2.4" stroke-linecap="round"/>
              <path d="M556 226 L560 228 L556 230 L557 228Z M552 227.4 L557.6 228.4" fill="#5A6070" stroke="#5A6070" stroke-width=".9" stroke-linecap="round" transform="rotate(-18 556 228)"/>
              <path d="M504 230 C500.8 226 500.8 222 504 221.4 C507.2 222 507.2 226 504 230Z" fill="#D9534A"/><circle cx="504" cy="224" r="1.1" fill="#FFF8EE"/><path d="M540 216 C536.8 212 536.8 208 540 207.4 C543.2 208 543.2 212 540 216Z" fill="#E2706A"/><circle cx="540" cy="210" r="1.1" fill="#FFF8EE"/><path d="M558 232 C554.8 228 554.8 224 558 223.4 C561.2 224 561.2 228 558 232Z" fill="#D9534A"/><circle cx="558" cy="226" r="1.1" fill="#FFF8EE"/>
              <polygon points="561.0,243.0 562.3,246.7 566.0,248.0 562.3,249.3 561.0,253.0 559.7,249.3 556.0,248.0 559.7,246.7" fill="#8A6A4A"/>
              <circle cx="561" cy="248" r="1" fill="#F7F0E1"/>
            </g>
            <rect x="504" y="186" width="22" height="8" fill="#F2B8C4" opacity=".75" transform="rotate(-14 515 190)"/>
            <rect x="538" y="186" width="22" height="8" fill="#BFDCCF" opacity=".75" transform="rotate(12 549 190)"/>
            <path d="M506 189 h18 M540 189 h18" stroke="#FFFFFF" stroke-width=".6" stroke-dasharray="1.4 1.6" opacity=".7"/>
          </g>
        </g>

        <!-- Framed certificate (illustrated); clicking opens the real photo -->
        <g class="obj" id="o-certificate" data-id="certificate" tabindex="0" role="button" aria-label="Framed certificate: Japanese, level N4">
          <rect x="501.4" y="302.4" width="53.2" height="77.2" fill="url(#gCert)"/>
          <path d="M501.4 302.4 H554.6 M501.4 302.4 V379.6" stroke="#000" stroke-width="1.2" opacity=".12"/>
          <g fill="#8A5A36">
            <path d="M527.0 310 C523.0 304 516.0 304 514.0 308 C518.0 306 522.0 307 523.0 311Z"/><path d="M529.0 310 C533.0 304 540.0 304 542.0 308 C538.0 306 534.0 307 533.0 311Z"/>
            <path d="M524.0 310 C520.0 307 516.0 309 517.0 312 C519.0 310 522.0 310 524.0 312Z"/><path d="M532.0 310 C536.0 307 540.0 309 539.0 312 C537.0 310 534.0 310 532.0 312Z"/>
          </g>
          <text x="528.0" y="319" text-anchor="middle" class="svg-cert" fill="#5A3B24">N4</text>
          <path d="M517.0 323.5 h22" stroke="#4A4A4A" stroke-width="1"/>
          <path d="M512.0 327.5 h32" stroke="#2A2A2A" stroke-width="1.5"/><path d="M512.0 331 h32" stroke="#2A2A2A" stroke-width="1.5"/>
          <path d="M506 337 h9" stroke="#6A6A6A" stroke-width="0.9"/><path d="M506 341 h9" stroke="#6A6A6A" stroke-width="0.9"/><path d="M506 345 h9" stroke="#6A6A6A" stroke-width="0.9"/>
          <path d="M520 337 h14" stroke="#6A6A6A" stroke-width="0.9"/><path d="M520 341 h10" stroke="#6A6A6A" stroke-width="0.9"/><path d="M520 345 h12" stroke="#6A6A6A" stroke-width="0.9"/>
          <path d="M514 351 h36" stroke="#7A7A7A" stroke-width="0.8"/><path d="M514 354 h36" stroke="#7A7A7A" stroke-width="0.8"/><path d="M514 357 h36" stroke="#7A7A7A" stroke-width="0.8"/><path d="M514 360 h26" stroke="#7A7A7A" stroke-width="0.8"/>
          <path d="M508 364 h40" stroke="#3A3A3A" stroke-width="0.9"/><path d="M508 367 h40" stroke="#3A3A3A" stroke-width="0.9"/><path d="M508 370 h30" stroke="#3A3A3A" stroke-width="0.9"/>
          <rect x="514" y="370.5" width="7" height="6.5" fill="none" stroke="#D2463E" stroke-width="1.1"/><rect x="535" y="370.5" width="7" height="6.5" fill="none" stroke="#D2463E" stroke-width="1.1"/>
          <path d="M515.5 372.5 h4 M515.5 374.5 h4 M536.5 372.5 h4 M536.5 374.5 h4" stroke="#D2463E" stroke-width=".6"/>
          <path d="M528.0 376 C525.0 373.5 524.0 375.5 525.0 377 C526.0 378 527.0 378 528.0 379 C529.0 378 530.0 378 531.0 377 C532.0 375.5 531.0 373.5 528.0 376Z" fill="#8A5A36"/>
          <path d="M501.4 326 L525 302.4 H533 L501.4 334Z" fill="#fff" opacity=".14"/>
          <path fill-rule="evenodd" d="M499 300 H557 V382 H499Z M501.4 302.4 V379.6 H554.6 V302.4Z" fill="#1E1F23"/>
          <rect x="499" y="300" width="58" height=".9" fill="#5A5C63"/>
          <circle cx="528.0" cy="295" r="2.6" fill="url(#gBrass)"/>
          <path d="M528.0 297 V301.6 Q528.0 304 530.6 303.4" stroke="#C9A04A" stroke-width="1.5" fill="none" stroke-linecap="round"/>
        </g>

        <!-- Wall clock: chunky red rim, gridded face -->
        <g class="obj" id="o-clock" data-id="clock" tabindex="0" role="button" aria-label="Wall clock: change the time of day">
          <clipPath id="clockFace"><circle cx="1084" cy="176" r="41"/></clipPath>
          <circle cx="1084" cy="176" r="55" fill="#B92A21"/>
          <circle cx="1082.5" cy="174.5" r="52.5" fill="#DC3B2E"/>
          <path d="M1037 164 A48 48 0 0 1 1094 129" stroke="#F36B5C" stroke-width="5" fill="none" stroke-linecap="round" opacity=".75"/>
          <path d="M1128 194 A47 47 0 0 1 1092 223" stroke="#A9241C" stroke-width="5" fill="none" stroke-linecap="round" opacity=".6"/>
          <circle cx="1084" cy="176" r="43.5" fill="#A5231B"/>
          <circle cx="1084" cy="176" r="41" fill="#F7EFE4"/>
          <path clip-path="url(#clockFace)" d="M1042.0 134 V218 M1046.6 134 V218 M1051.2 134 V218 M1055.8 134 V218 M1060.4 134 V218 M1065.0 134 V218 M1069.6 134 V218 M1074.2 134 V218 M1078.8 134 V218 M1083.4 134 V218 M1088.0 134 V218 M1092.6 134 V218 M1097.2 134 V218 M1101.8 134 V218 M1106.4 134 V218 M1111.0 134 V218 M1115.6 134 V218 M1120.2 134 V218 M1124.8 134 V218 M1042 134.0 H1126 M1042 138.6 H1126 M1042 143.2 H1126 M1042 147.8 H1126 M1042 152.4 H1126 M1042 157.0 H1126 M1042 161.6 H1126 M1042 166.2 H1126 M1042 170.8 H1126 M1042 175.4 H1126 M1042 180.0 H1126 M1042 184.6 H1126 M1042 189.2 H1126 M1042 193.8 H1126 M1042 198.4 H1126 M1042 203.0 H1126 M1042 207.6 H1126 M1042 212.2 H1126 M1042 216.8 H1126" stroke="#D9473A" stroke-width=".45" opacity=".45"/>
          <path d="M1043 176 A41 41 0 0 1 1084 135" stroke="#000" stroke-width="3" fill="none" opacity=".07"/>
          <g fill="#D3372B"><text x="1099.5" y="149.7" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">1</text><text x="1110.8" y="161.0" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">2</text><text x="1115.0" y="176.5" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">3</text><text x="1110.8" y="192.0" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">4</text><text x="1099.5" y="203.3" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">5</text><text x="1084.0" y="207.5" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">6</text><text x="1068.5" y="203.3" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">7</text><text x="1057.2" y="192.0" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">8</text><text x="1053.0" y="176.5" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">9</text><text x="1057.2" y="161.0" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">10</text><text x="1068.5" y="149.7" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">11</text><text x="1084.0" y="145.5" class="svg-clocknum" text-anchor="middle" dominant-baseline="central">12</text></g>
          <text x="1084" y="190" text-anchor="middle" class="svg-quartz" fill="#D3372B">quartz</text>
          <path id="hand-h" d="M1084 182 V156" stroke="#D3372B" stroke-width="4.6" stroke-linecap="round"/>
          <path id="hand-m" d="M1084 184 V143" stroke="#D3372B" stroke-width="3" stroke-linecap="round"/>
          <g class="sec"><path d="M1084 186 V140" stroke="#D3372B" stroke-width=".9" stroke-linecap="round"/></g>
          <circle cx="1084" cy="176" r="3.4" fill="#D3372B"/><circle cx="1083.2" cy="175.2" r="1" fill="#F7A59B"/>
        </g>

        <!-- Calendar: art card with a painted sunflower picture; JS fills in this month -->
        <g class="obj" id="o-calendar" transform="translate(0 -14)" data-id="calendar" tabindex="0" role="button" aria-label="Calendar: my experience">
          <clipPath id="calWin"><rect x="1039" y="285" width="78" height="56" rx="3"/></clipPath>
          <path d="M1078 268 L1071 282 M1078 268 L1085 282" stroke="#B89A68" stroke-width=".9" fill="none"/>
          <circle cx="1078" cy="267" r="2.8" fill="url(#gBrass)"/>
          <rect x="1034" y="280" width="88" height="122" rx="5" fill="url(#gCalCard)"/>
          <rect x="1034" y="399" width="88" height="3" rx="1.5" fill="#000" opacity=".05"/>
          <g clip-path="url(#calWin)">
            <rect x="1039" y="285" width="78" height="56" fill="url(#gCalSky)"/>
            <path d="M1092 290 C1100 286 1110 290 1116 288 M1040 298 C1046 295 1054 297 1058 295" stroke="#fff" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".6"/>
            <path d="M1050 324 C1052 336 1048 346 1050 346" stroke="#3E6B33" stroke-width="2.2" fill="none"/><path d="M1066 306 C1068 318 1064 328 1066 346" stroke="#3E6B33" stroke-width="2.2" fill="none"/><path d="M1085 320 C1087 332 1083 342 1085 346" stroke="#3E6B33" stroke-width="2.2" fill="none"/><path d="M1104 300 C1106 312 1102 322 1104 346" stroke="#3E6B33" stroke-width="2.2" fill="none"/><path d="M1100 336 C1102 348 1098 358 1100 346" stroke="#3E6B33" stroke-width="2.2" fill="none"/><path d="M1118 318 C1120 330 1116 340 1118 346" stroke="#3E6B33" stroke-width="2.2" fill="none"/><ellipse cx="1046" cy="336" rx="8" ry="3.4" transform="rotate(-25 1046 336)" fill="#2F5A2B"/><ellipse cx="1060" cy="330" rx="8" ry="3.4" transform="rotate(30 1060 330)" fill="#3E6B33"/><ellipse cx="1078" cy="334" rx="8" ry="3.4" transform="rotate(-35 1078 334)" fill="#2F5A2B"/><ellipse cx="1094" cy="326" rx="8" ry="3.4" transform="rotate(25 1094 326)" fill="#3E6B33"/><ellipse cx="1110" cy="340" rx="8" ry="3.4" transform="rotate(-20 1110 340)" fill="#2F5A2B"/><ellipse cx="1070" cy="342" rx="8" ry="3.4" transform="rotate(15 1070 342)" fill="#4C7A3A"/>
            <ellipse cx="1055.0" cy="324.0" rx="2.9" ry="1.2" transform="rotate(0 1055.0 324.0)" fill="#E9A923"/><ellipse cx="1054.5" cy="326.2" rx="2.9" ry="1.2" transform="rotate(26 1054.5 326.2)" fill="#F6C836"/><ellipse cx="1053.1" cy="327.9" rx="2.9" ry="1.2" transform="rotate(51 1053.1 327.9)" fill="#E9A923"/><ellipse cx="1051.1" cy="328.9" rx="2.9" ry="1.2" transform="rotate(77 1051.1 328.9)" fill="#F6C836"/><ellipse cx="1048.9" cy="328.9" rx="2.9" ry="1.2" transform="rotate(103 1048.9 328.9)" fill="#E9A923"/><ellipse cx="1046.9" cy="327.9" rx="2.9" ry="1.2" transform="rotate(129 1046.9 327.9)" fill="#F6C836"/><ellipse cx="1045.5" cy="326.2" rx="2.9" ry="1.2" transform="rotate(154 1045.5 326.2)" fill="#E9A923"/><ellipse cx="1045.0" cy="324.0" rx="2.9" ry="1.2" transform="rotate(180 1045.0 324.0)" fill="#F6C836"/><ellipse cx="1045.5" cy="321.8" rx="2.9" ry="1.2" transform="rotate(206 1045.5 321.8)" fill="#E9A923"/><ellipse cx="1046.9" cy="320.1" rx="2.9" ry="1.2" transform="rotate(231 1046.9 320.1)" fill="#F6C836"/><ellipse cx="1048.9" cy="319.1" rx="2.9" ry="1.2" transform="rotate(257 1048.9 319.1)" fill="#E9A923"/><ellipse cx="1051.1" cy="319.1" rx="2.9" ry="1.2" transform="rotate(283 1051.1 319.1)" fill="#F6C836"/><ellipse cx="1053.1" cy="320.1" rx="2.9" ry="1.2" transform="rotate(309 1053.1 320.1)" fill="#E9A923"/><ellipse cx="1054.5" cy="321.8" rx="2.9" ry="1.2" transform="rotate(334 1054.5 321.8)" fill="#F6C836"/><circle cx="1050" cy="324" r="2.9" fill="#4A2C14"/><circle cx="1049.3" cy="323.3" r="1.4" fill="#6B4220"/><ellipse cx="1071.8" cy="306.0" rx="3.4" ry="1.4" transform="rotate(0 1071.8 306.0)" fill="#E9A923"/><ellipse cx="1071.2" cy="308.5" rx="3.4" ry="1.4" transform="rotate(26 1071.2 308.5)" fill="#F6C836"/><ellipse cx="1069.6" cy="310.5" rx="3.4" ry="1.4" transform="rotate(51 1069.6 310.5)" fill="#E9A923"/><ellipse cx="1067.3" cy="311.6" rx="3.4" ry="1.4" transform="rotate(77 1067.3 311.6)" fill="#F6C836"/><ellipse cx="1064.7" cy="311.6" rx="3.4" ry="1.4" transform="rotate(103 1064.7 311.6)" fill="#E9A923"/><ellipse cx="1062.4" cy="310.5" rx="3.4" ry="1.4" transform="rotate(129 1062.4 310.5)" fill="#F6C836"/><ellipse cx="1060.8" cy="308.5" rx="3.4" ry="1.4" transform="rotate(154 1060.8 308.5)" fill="#E9A923"/><ellipse cx="1060.2" cy="306.0" rx="3.4" ry="1.4" transform="rotate(180 1060.2 306.0)" fill="#F6C836"/><ellipse cx="1060.8" cy="303.5" rx="3.4" ry="1.4" transform="rotate(206 1060.8 303.5)" fill="#E9A923"/><ellipse cx="1062.4" cy="301.5" rx="3.4" ry="1.4" transform="rotate(231 1062.4 301.5)" fill="#F6C836"/><ellipse cx="1064.7" cy="300.4" rx="3.4" ry="1.4" transform="rotate(257 1064.7 300.4)" fill="#E9A923"/><ellipse cx="1067.3" cy="300.4" rx="3.4" ry="1.4" transform="rotate(283 1067.3 300.4)" fill="#F6C836"/><ellipse cx="1069.6" cy="301.5" rx="3.4" ry="1.4" transform="rotate(309 1069.6 301.5)" fill="#E9A923"/><ellipse cx="1071.2" cy="303.5" rx="3.4" ry="1.4" transform="rotate(334 1071.2 303.5)" fill="#F6C836"/><circle cx="1066" cy="306" r="3.4" fill="#4A2C14"/><circle cx="1065.2" cy="305.2" r="1.6" fill="#6B4220"/><ellipse cx="1090.4" cy="320.0" rx="3.1" ry="1.3" transform="rotate(0 1090.4 320.0)" fill="#E9A923"/><ellipse cx="1089.9" cy="322.3" rx="3.1" ry="1.3" transform="rotate(26 1089.9 322.3)" fill="#F6C836"/><ellipse cx="1088.4" cy="324.2" rx="3.1" ry="1.3" transform="rotate(51 1088.4 324.2)" fill="#E9A923"/><ellipse cx="1086.2" cy="325.3" rx="3.1" ry="1.3" transform="rotate(77 1086.2 325.3)" fill="#F6C836"/><ellipse cx="1083.8" cy="325.3" rx="3.1" ry="1.3" transform="rotate(103 1083.8 325.3)" fill="#E9A923"/><ellipse cx="1081.6" cy="324.2" rx="3.1" ry="1.3" transform="rotate(129 1081.6 324.2)" fill="#F6C836"/><ellipse cx="1080.1" cy="322.3" rx="3.1" ry="1.3" transform="rotate(154 1080.1 322.3)" fill="#E9A923"/><ellipse cx="1079.6" cy="320.0" rx="3.1" ry="1.3" transform="rotate(180 1079.6 320.0)" fill="#F6C836"/><ellipse cx="1080.1" cy="317.7" rx="3.1" ry="1.3" transform="rotate(206 1080.1 317.7)" fill="#E9A923"/><ellipse cx="1081.6" cy="315.8" rx="3.1" ry="1.3" transform="rotate(231 1081.6 315.8)" fill="#F6C836"/><ellipse cx="1083.8" cy="314.7" rx="3.1" ry="1.3" transform="rotate(257 1083.8 314.7)" fill="#E9A923"/><ellipse cx="1086.2" cy="314.7" rx="3.1" ry="1.3" transform="rotate(283 1086.2 314.7)" fill="#F6C836"/><ellipse cx="1088.4" cy="315.8" rx="3.1" ry="1.3" transform="rotate(309 1088.4 315.8)" fill="#E9A923"/><ellipse cx="1089.9" cy="317.7" rx="3.1" ry="1.3" transform="rotate(334 1089.9 317.7)" fill="#F6C836"/><circle cx="1085" cy="320" r="3.1" fill="#4A2C14"/><circle cx="1084.2" cy="319.2" r="1.5" fill="#6B4220"/><ellipse cx="1108.7" cy="300.0" rx="2.7" ry="1.1" transform="rotate(0 1108.7 300.0)" fill="#E9A923"/><ellipse cx="1108.2" cy="302.0" rx="2.7" ry="1.1" transform="rotate(26 1108.2 302.0)" fill="#F6C836"/><ellipse cx="1106.9" cy="303.7" rx="2.7" ry="1.1" transform="rotate(51 1106.9 303.7)" fill="#E9A923"/><ellipse cx="1105.0" cy="304.6" rx="2.7" ry="1.1" transform="rotate(77 1105.0 304.6)" fill="#F6C836"/><ellipse cx="1103.0" cy="304.6" rx="2.7" ry="1.1" transform="rotate(103 1103.0 304.6)" fill="#E9A923"/><ellipse cx="1101.1" cy="303.7" rx="2.7" ry="1.1" transform="rotate(129 1101.1 303.7)" fill="#F6C836"/><ellipse cx="1099.8" cy="302.0" rx="2.7" ry="1.1" transform="rotate(154 1099.8 302.0)" fill="#E9A923"/><ellipse cx="1099.3" cy="300.0" rx="2.7" ry="1.1" transform="rotate(180 1099.3 300.0)" fill="#F6C836"/><ellipse cx="1099.8" cy="298.0" rx="2.7" ry="1.1" transform="rotate(206 1099.8 298.0)" fill="#E9A923"/><ellipse cx="1101.1" cy="296.3" rx="2.7" ry="1.1" transform="rotate(231 1101.1 296.3)" fill="#F6C836"/><ellipse cx="1103.0" cy="295.4" rx="2.7" ry="1.1" transform="rotate(257 1103.0 295.4)" fill="#E9A923"/><ellipse cx="1105.0" cy="295.4" rx="2.7" ry="1.1" transform="rotate(283 1105.0 295.4)" fill="#F6C836"/><ellipse cx="1106.9" cy="296.3" rx="2.7" ry="1.1" transform="rotate(309 1106.9 296.3)" fill="#E9A923"/><ellipse cx="1108.2" cy="298.0" rx="2.7" ry="1.1" transform="rotate(334 1108.2 298.0)" fill="#F6C836"/><circle cx="1104" cy="300" r="2.7" fill="#4A2C14"/><circle cx="1103.3" cy="299.4" r="1.3" fill="#6B4220"/><ellipse cx="1104.3" cy="336.0" rx="2.5" ry="1.0" transform="rotate(0 1104.3 336.0)" fill="#E9A923"/><ellipse cx="1103.9" cy="337.9" rx="2.5" ry="1.0" transform="rotate(26 1103.9 337.9)" fill="#F6C836"/><ellipse cx="1102.7" cy="339.4" rx="2.5" ry="1.0" transform="rotate(51 1102.7 339.4)" fill="#E9A923"/><ellipse cx="1101.0" cy="340.2" rx="2.5" ry="1.0" transform="rotate(77 1101.0 340.2)" fill="#F6C836"/><ellipse cx="1099.0" cy="340.2" rx="2.5" ry="1.0" transform="rotate(103 1099.0 340.2)" fill="#E9A923"/><ellipse cx="1097.3" cy="339.4" rx="2.5" ry="1.0" transform="rotate(129 1097.3 339.4)" fill="#F6C836"/><ellipse cx="1096.1" cy="337.9" rx="2.5" ry="1.0" transform="rotate(154 1096.1 337.9)" fill="#E9A923"/><ellipse cx="1095.7" cy="336.0" rx="2.5" ry="1.0" transform="rotate(180 1095.7 336.0)" fill="#F6C836"/><ellipse cx="1096.1" cy="334.1" rx="2.5" ry="1.0" transform="rotate(206 1096.1 334.1)" fill="#E9A923"/><ellipse cx="1097.3" cy="332.6" rx="2.5" ry="1.0" transform="rotate(231 1097.3 332.6)" fill="#F6C836"/><ellipse cx="1099.0" cy="331.8" rx="2.5" ry="1.0" transform="rotate(257 1099.0 331.8)" fill="#E9A923"/><ellipse cx="1101.0" cy="331.8" rx="2.5" ry="1.0" transform="rotate(283 1101.0 331.8)" fill="#F6C836"/><ellipse cx="1102.7" cy="332.6" rx="2.5" ry="1.0" transform="rotate(309 1102.7 332.6)" fill="#E9A923"/><ellipse cx="1103.9" cy="334.1" rx="2.5" ry="1.0" transform="rotate(334 1103.9 334.1)" fill="#F6C836"/><circle cx="1100" cy="336" r="2.5" fill="#4A2C14"/><circle cx="1099.4" cy="335.4" r="1.2" fill="#6B4220"/><ellipse cx="1122.3" cy="318.0" rx="2.5" ry="1.0" transform="rotate(0 1122.3 318.0)" fill="#E9A923"/><ellipse cx="1121.9" cy="319.9" rx="2.5" ry="1.0" transform="rotate(26 1121.9 319.9)" fill="#F6C836"/><ellipse cx="1120.7" cy="321.4" rx="2.5" ry="1.0" transform="rotate(51 1120.7 321.4)" fill="#E9A923"/><ellipse cx="1119.0" cy="322.2" rx="2.5" ry="1.0" transform="rotate(77 1119.0 322.2)" fill="#F6C836"/><ellipse cx="1117.0" cy="322.2" rx="2.5" ry="1.0" transform="rotate(103 1117.0 322.2)" fill="#E9A923"/><ellipse cx="1115.3" cy="321.4" rx="2.5" ry="1.0" transform="rotate(129 1115.3 321.4)" fill="#F6C836"/><ellipse cx="1114.1" cy="319.9" rx="2.5" ry="1.0" transform="rotate(154 1114.1 319.9)" fill="#E9A923"/><ellipse cx="1113.7" cy="318.0" rx="2.5" ry="1.0" transform="rotate(180 1113.7 318.0)" fill="#F6C836"/><ellipse cx="1114.1" cy="316.1" rx="2.5" ry="1.0" transform="rotate(206 1114.1 316.1)" fill="#E9A923"/><ellipse cx="1115.3" cy="314.6" rx="2.5" ry="1.0" transform="rotate(231 1115.3 314.6)" fill="#F6C836"/><ellipse cx="1117.0" cy="313.8" rx="2.5" ry="1.0" transform="rotate(257 1117.0 313.8)" fill="#E9A923"/><ellipse cx="1119.0" cy="313.8" rx="2.5" ry="1.0" transform="rotate(283 1119.0 313.8)" fill="#F6C836"/><ellipse cx="1120.7" cy="314.6" rx="2.5" ry="1.0" transform="rotate(309 1120.7 314.6)" fill="#E9A923"/><ellipse cx="1121.9" cy="316.1" rx="2.5" ry="1.0" transform="rotate(334 1121.9 316.1)" fill="#F6C836"/><circle cx="1118" cy="318" r="2.5" fill="#4A2C14"/><circle cx="1117.4" cy="317.4" r="1.2" fill="#6B4220"/>
          </g>
          <rect x="1070" y="276" width="16" height="9" rx="1.6" fill="#3B3F48"/>
          <rect x="1070" y="276" width="16" height="2.4" rx="1.2" fill="#6C717C"/>
          <text x="1040" y="350" class="svg-calnote">Helianthus</text>
          <text x="1040" y="354.4" class="svg-calnote">annuus</text>
          <text x="1040" y="358.8" class="svg-calnote">/ Sunflower</text>
          <text id="cal-mnum" x="1040" y="384" class="svg-calnum">01</text>
          <text id="cal-mname" x="1039" y="395" class="svg-calmonth">Jan.</text>
          <g id="cal-days"></g>
        </g>''')

w('''
        <!-- Walnut frame with a little doodle, keys hanging below -->
        <g transform="translate(-4 -20)">
        <g class="c-sm">
          <rect x="1040" y="416" width="78" height="56" rx="6" fill="url(#gWalnut)"/>
          <path d="M1040 422 Q1040 416 1046 416 H1112 Q1118 416 1118 422 L1110 424 H1048Z" fill="#C9844F" opacity=".7"/>
          <rect x="1048" y="424" width="62" height="40" rx="2" fill="#FFFDF7"/>
          <rect x="1048" y="424" width="62" height="3" fill="#000" opacity=".06"/>
          <!-- couple portrait: the two characters from the reference illustration, set close together -->
          <rect x="1066" y="433.5" width="27" height="21" fill="#FFFFFF" stroke="#E2DBCF" stroke-width=".5"/>
          <image href="assets/couple.png" x="1067.2" y="434.6" width="24.6" height="19.4" preserveAspectRatio="xMidYMax meet"/>
        </g>
        <g class="c-sm keys" style="--o:1079px 474px">
          <path d="M1060 472 V478 C1060 482 1066 482 1066 478" stroke="#D8B25A" stroke-width="1.8" fill="none" stroke-linecap="round"/>
          <path d="M1098 472 V478 C1098 482 1104 482 1104 478" stroke="#D8B25A" stroke-width="1.8" fill="none" stroke-linecap="round"/>
          <circle cx="1061" cy="487" r="5.5" fill="none" stroke="#B9BDC4" stroke-width="1.4"/>
          <path d="M1060 492 V512 L1062 514 L1063 510 L1062 506 L1063 502 V492Z" fill="url(#gBrass)"/>
          <rect x="1057" y="490" width="7" height="5" rx="1.5" fill="url(#gBrass)"/>
          <circle cx="1099" cy="487" r="5.5" fill="none" stroke="#B9BDC4" stroke-width="1.4"/>
          <rect x="1092" y="494" width="10" height="20" rx="4" fill="#24272E"/>
          <rect x="1094" y="497" width="3" height="6" rx="1.5" fill="#4A4F5A"/>
          <path d="M1102 492 L1104 500" stroke="#B9BDC4" stroke-width="1.2"/>
          <path d="M1105 512 C1100 507 1099 503 1102 502 C1104 501 1105 503 1105 503 C1105 503 1106 501 1108 502 C1111 503 1110 507 1105 512Z" fill="#9A5BD6"/>
          <path d="M1102.5 504 L1104 503" stroke="#E5D2F7" stroke-width="1" stroke-linecap="round"/>
        </g>
        </g>''')
w('''
        <!-- Floor lamp: smoked-glass drum shade on a slim bronze pole -->
        <g id="lamp-floor" class="c-sm" transform="translate(-22 0)">
          <ellipse cx="90" cy="797" rx="34" ry="5" fill="#4E3320" opacity=".22" filter="url(#edge1)"/>
          <path d="M64 789 V793 A26 4.6 0 0 0 116 793 V789Z" fill="url(#gBronze)"/>
          <ellipse cx="90" cy="789" rx="26" ry="4.6" fill="#4A4038"/>
          <ellipse cx="88" cy="788.4" rx="16" ry="2" fill="#6E6256" opacity=".7"/>
          <rect x="87.6" y="784" width="4.8" height="5" rx="1" fill="#8C7E6E"/>
          <rect x="88.6" y="358" width="2.8" height="428" fill="url(#gBronze)"/>
          <rect x="88.9" y="358" width=".9" height="428" fill="#A0907C" opacity=".7"/>
          <g transform="translate(0 58)">
          <path d="M54 297 H126 Q132 297 132 303 V324 Q132 330 126 330 H54 Q48 330 48 324 V303 Q48 297 54 297Z" fill="#6F6A65" opacity=".46"/>
          <ellipse cx="90" cy="297.5" rx="40" ry="3.6" fill="#8E8984" opacity=".45"/>
          <ellipse cx="90" cy="329.4" rx="40" ry="3.4" fill="none" stroke="#5C5752" stroke-width="1" opacity=".6"/>
          <ellipse cx="90" cy="303.5" rx="15" ry="2.6" fill="#E7DFD2"/>
          <ellipse cx="90" cy="315" rx="10" ry="2" fill="#D6CCBC"/>
          <path d="M55 301 V325 M59 300 V326" stroke="#FFFFFF" stroke-width="1.6" opacity=".35" stroke-linecap="round"/>
          <path d="M123 301 V325" stroke="#FFFFFF" stroke-width="1.2" opacity=".25" stroke-linecap="round"/>
          <rect x="89" y="294.6" width="2" height="3" rx=".6" fill="#4A4038"/>
          </g>
        </g>''')
# ------------------------------------------------------------------ bookshelf
w('<g transform="translate(0 30)">')
K = 0.09
w('''
        <!-- ===== Bookshelf ===== -->
        <g class="c-lg">''')
side = [(470, 300), back(470, 300, K), back(470, 772, K), (470, 772)]
w('          ' + poly(side, 'url(#gOakSide)'))
w('          <rect x="140" y="300" width="330" height="454" rx="3" fill="url(#gOakF)"/>')
rows = [(316, 412), (420, 520), (528, 632), (640, 748)]
cols = [(156, 300), (308, 454)]
for (y0, y1) in rows:
    for (x0, x1) in cols:
        b0 = back(x0, y0, K); b1 = back(x1, y1, K)
        bx0, by0 = b0; bx1, by1 = b1
        w('          ' + f'<rect x="{bx0}" y="{by0}" width="{round(bx1 - bx0, 1)}" height="{round(by1 - by0, 1)}" fill="url(#gCBack)"/>')
        w('          ' + poly([(x0, y0), (x1, y0), (bx1, by0), (bx0, by0)], 'url(#gInTop)'))
        w('          ' + poly([(x0, y0), (bx0, by0), (bx0, by1), (x0, y1)], 'url(#gInL)'))
        w('          ' + poly([(x1, y0), (bx1, by0), (bx1, by1), (x1, y1)], 'url(#gInR)'))
        if by1 < y1:
            w('          ' + poly([(x0, y1), (x1, y1), (bx1, by1), (bx0, by1)], 'url(#gOakTop)'))
        w(f'          <rect x="{bx0}" y="{by0}" width="{round(bx1 - bx0, 1)}" height="16" fill="url(#gCelShade)"/>')
for y in [412, 520, 632]:
    w(f'          <rect x="156" y="{y}" width="298" height="8" fill="url(#gOakEdge)"/><path d="M156 {y + 1.6} H454" stroke="#D9AE85" stroke-width=".7" opacity=".8"/><path d="M156 {y + 5.8} H454" stroke="#4C2F1D" stroke-width=".8" opacity=".45"/>')
w('''          <rect x="300" y="316" width="8" height="432" fill="#7E5134"/><rect x="300" y="316" width="2" height="432" fill="#A87754" opacity=".7"/>
          <rect x="140" y="300" width="330" height="3" rx="1.5" fill="#D9AE85" opacity=".75"/>
          <rect x="140" y="300" width="3" height="472" fill="#D9AE85" opacity=".55"/>
          <path d="M145.5 334 V742 M150.5 334 V742 M459.5 334 V742 M464.5 334 V742" stroke="#4C2F1D" stroke-width="1.3" opacity=".55"/>
          <path d="M146.7 334 V742 M151.7 334 V742 M460.7 334 V742 M465.7 334 V742" stroke="#B07D57" stroke-width=".7" opacity=".55"/>
          <rect x="141" y="316" width="14" height="14" rx="1" fill="#6E4529"/><rect x="141" y="316" width="14" height="1" fill="#B07D57" opacity=".7"/><circle cx="148" cy="323" r="4.8" fill="#9A6848"/><circle cx="148" cy="323" r="2.4" fill="#5A3823"/><circle cx="147" cy="322" r="1" fill="#D9AE85" opacity=".8"/><rect x="455" y="316" width="14" height="14" rx="1" fill="#6E4529"/><rect x="455" y="316" width="14" height="1" fill="#B07D57" opacity=".7"/><circle cx="462" cy="323" r="4.8" fill="#9A6848"/><circle cx="462" cy="323" r="2.4" fill="#5A3823"/><circle cx="461" cy="322" r="1" fill="#D9AE85" opacity=".8"/>
          <!-- base: moulding, scalloped apron, bracket feet -->
          <rect x="150" y="756" width="310" height="16" fill="#2E1D12" opacity=".55"/>
          <rect x="138" y="748" width="334" height="7" rx="1.5" fill="url(#gOakEdge)"/>
          <path d="M138 749.4 H472" stroke="#D9AE85" stroke-width=".8" opacity=".8"/>
          <path d="M140 754 H470 V772 H460 C455 772 452 765 444 763 C426 760 404 766 384 764 C362 762 336 758 305 758 C274 758 248 762 226 764 C206 766 184 760 166 763 C158 765 155 772 150 772 H140Z" fill="url(#gOakF)"/>
          <path d="M460 772 C455 772 452 765 444 763 C426 760 404 766 384 764 C362 762 336 758 305 758 C274 758 248 762 226 764 C206 766 184 760 166 763 C158 765 155 772 150 772" fill="none" stroke="#B07D57" stroke-width=".9" opacity=".8"/>
          <path d="M140 755 H470" stroke="#3E2616" stroke-width="1" opacity=".5"/>
          <!-- crown moulding -->
          <rect x="132" y="300" width="346" height="5.4" rx="1.5" fill="url(#gOakEdge)"/>
          <path d="M132 300.8 H478" stroke="#E2B98F" stroke-width=".9" opacity=".85"/>
          <path d="M135 305.4 H475 L471 311 H139Z" fill="#6A4229"/>
          <rect x="139" y="311" width="332" height="3.4" fill="#9A6848"/>
          <path d="M139 311.6 H471" stroke="#C99A70" stroke-width=".6" opacity=".8"/>
        </g>''')

def book(x, ybot, wd, h, col, label='', rot=0, pivot=None):
    t = f' transform="rotate({rot} {pivot[0]} {pivot[1]})"' if rot else ''
    s = f'<g{t}><rect x="{x}" y="{ybot - h}" width="{wd}" height="{h}" rx="1.6" fill="{col}"/>'
    s += f'<rect x="{x}" y="{ybot - h}" width="{wd}" height="{h}" rx="1.6" fill="url(#gShadeH)"/>'
    s += f'<rect x="{x}" y="{ybot - h + 8}" width="{wd}" height="2.5" fill="#fff" opacity=".55"/>'
    s += f'<rect x="{x}" y="{ybot - 12}" width="{wd}" height="2.5" fill="#fff" opacity=".55"/>'
    if label:
        cx = x + wd / 2; cy = ybot - h / 2
        s += f'<text x="{cx}" y="{cy}" class="svg-spine" text-anchor="middle" dominant-baseline="middle" transform="rotate(-90 {cx} {cy})">{label}</text>'
    return s + '</g>'
def flatbook(x, ybot, wd, h, col):
    return (f'<rect x="{x}" y="{ybot - h}" width="{wd}" height="{h}" rx="1.6" fill="{col}"/>'
            f'<rect x="{x}" y="{ybot - h}" width="{wd}" height="{h}" rx="1.6" fill="url(#gShadeV)"/>'
            f'<rect x="{x + wd - 5}" y="{ybot - h + 2}" width="3" height="{h - 4}" fill="#FFFDF5" opacity=".8"/>')

def vine(pts_path, leaves, o, t, dl):
    s = f'<g class="vine c-plant" style="--o:{o}; --t:{t}s; --dl:{dl}s"><path d="{pts_path}" stroke="#5E8A55" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
    for i, (x, y, r, sc) in enumerate(leaves):
        g = ['url(#gLeaf)', 'url(#gLeafB)', 'url(#gLeafC)'][i % 3]
        s += f'<use href="#hleaf" transform="translate({x} {y}) rotate({r}) scale({sc})" fill="{g}"/>'
    return s + '</g>'

# --- top of bookshelf: string-of-pearls, books, pilea
import math, random
rnd = random.Random(11)
def cubic(p0, p1, p2, p3, t):
    mt = 1 - t
    return (mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0],
            mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1])
def beads_along(p0, p1, p2, p3, gap=6.6):
    pts = [cubic(p0, p1, p2, p3, i / 400) for i in range(401)]
    res = [pts[0]]; acc = 0
    for q0, q1 in zip(pts, pts[1:]):
        acc += math.dist(q0, q1)
        if acc >= gap: res.append(q1); acc = 0
    return res
def bead(x, y, r):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="url(#gPearl)"/>'
            f'<circle cx="{x - r * .38:.1f}" cy="{y - r * .38:.1f}" r="{r * .3:.1f}" fill="#E6F8CC"/>')
def pearls(strands, o, t, dl):
    out_ = f'<g class="vine c-plant" style="--o:{o}; --t:{t}s; --dl:{dl}s">'
    for (p0, p1, p2, p3) in strands:
        out_ += f'<path d="M{p0[0]} {p0[1]} C{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]}" stroke="#6E9F4E" stroke-width="1.1" fill="none"/>'
        for (x, y) in beads_along(p0, p1, p2, p3)[1:]:
            out_ += bead(x + rnd.uniform(-1, 1), y, round(rnd.uniform(2.7, 3.7), 1))
    return out_ + '</g>'

# pothos in a ribbed cream pot: a full bunch on top, long vines trailing down the shelf
def pleaf(x, y, ang, sc, grad):
    return f'<use href="#pleaf" transform="translate({x:.1f} {y:.1f}) rotate({ang:.0f}) scale({sc:.2f})" fill="url(#{grad})"/>'
PG = ['gPothos', 'gPothosB', 'gPothosC']
def vine_leaves(p0, p1, p2, p3, start_sc, o, t, dl):
    pts = [cubic(p0, p1, p2, p3, i / 300) for i in range(301)]
    nodes = []; acc = 0
    for q0, q1 in zip(pts, pts[1:]):
        acc += math.dist(q0, q1)
        if acc >= 24: nodes.append(q1); acc = 0
    g = f'<g class="vine c-plant" style="--o:{o}; --t:{t}s; --dl:{dl}s">'
    g += f'<path d="M{p0[0]} {p0[1]} C{p1[0]} {p1[1]} {p2[0]} {p2[1]} {p3[0]} {p3[1]}" stroke="#5E9440" stroke-width="2" fill="none" stroke-linecap="round"/>'
    n = len(nodes)
    for i, (x, y) in enumerate(nodes):
        side = -1 if i % 2 else 1
        sc = start_sc - (start_sc - .3) * i / max(1, n - 1)
        g += f'<path d="M{x:.1f} {y:.1f} l{side * 6} 4" stroke="#5E9440" stroke-width="1.4"/>'
        g += pleaf(x + side * 6, y + 4, 180 + side * rnd.uniform(28, 50), sc, PG[i % 3])
    g += pleaf(p3[0], p3[1], 180 + rnd.uniform(-10, 10), .3, 'gPothosB')
    return g + '</g>'

# back of the bunch
back_ = ''
for i in range(9):
    ang = -80 + i * 20 + rnd.uniform(-6, 6)
    bx = 188 + math.sin(math.radians(ang)) * 16; by = 262 - math.cos(math.radians(ang)) * 12
    back_ += f'<path d="M{188 + math.sin(math.radians(ang)) * 3:.1f} 266 L{bx:.1f} {by:.1f}" stroke="#5E9440" stroke-width="1.6"/>'
    back_ += pleaf(bx, by, ang, rnd.uniform(.62, .8), PG[i % 3])
w(f'        <g class="plant-up c-plant" style="--o:188px 266px; --t:5.2s">{back_}</g>')
# trailing vines (behind the pot rim, in front of the shelf)
w('        ' + vine_leaves((166, 266), (140, 300), (126, 430), (136, 590), .62, '166px 266px', 6.6, 0))
w('        ' + vine_leaves((172, 268), (154, 320), (150, 420), (158, 500), .58, '172px 268px', 7.4, -2))
w('        ' + vine_leaves((200, 270), (206, 306), (198, 352), (206, 400), .5, '200px 270px', 6.1, -3.5))
# ribbed cream pot
ribs = ' '.join(f'M{x} 266 L{x + (0 if x == 188 else (1 if x > 188 else -1)) * 1.5:.1f} 296' for x in range(164, 214, 4))
w(f'''        <g class="c-sm">
          <path d="M160 262 H216 L212 294 Q211 300 205 300 H171 Q165 300 164 294Z" fill="url(#gCeramic)"/>
          <path d="{ribs}" stroke="#D3C8B6" stroke-width="1.3"/>
          <path d="{' '.join(f'M{x + 1.6} 266 L{x + 1.6} 294' for x in range(164, 212, 4))}" stroke="#FFFFFF" stroke-width=".9" opacity=".8"/>
          <rect x="166" y="294" width="44" height="6" rx="2" fill="#E6DCCB"/>
          <rect x="158" y="259" width="60" height="6" rx="3" fill="#FBF7EF"/>
          <ellipse cx="188" cy="261" rx="27" ry="2.6" fill="#5C4230"/>
        </g>''')
# leaves spilling over the front of the rim
front_ = ''
for ang, bx, sc, g in [(-118, 168, .6, 'gPothos'), (-150, 176, .52, 'gPothosB'), (134, 204, .58, 'gPothosC'), (162, 196, .5, 'gPothos'), (-30, 182, .55, 'gPothosB'), (26, 196, .6, 'gPothos')]:
    front_ += pleaf(bx, 264, ang, sc, g)
w(f'        <g class="plant-up c-plant" style="--o:188px 266px; --t:4.6s; --dl:-1s">{front_}</g>')

w('''        <!-- Mushroom lamp: glossy red, to match the wall clock -->
        <g id="lamp-mush" class="c-sm" transform="translate(438 299) scale(1.25) translate(-316 -299)">
          <ellipse cx="316" cy="298.4" rx="17" ry="2.6" fill="#6E1A15"/>
          <path d="M299 298 Q300 294.5 305 294 H327 Q332 294.5 333 298Z" fill="url(#gRedBase)"/>
          <path d="M305 294.5 C311 290 313.4 282 314 270 H318 C318.6 282 321 290 327 294.5Z" fill="url(#gRedBase)"/>
          <path d="M315 272 C314.6 282 313 289 309 293.5" stroke="#F07A6C" stroke-width="1" fill="none" opacity=".7"/>
          <path d="M288 266 C288 252 302 244 316 244 C330 244 344 252 344 266 C344 270 337 271.5 316 271.5 C295 271.5 288 270 288 266Z" fill="url(#gRedDome)"/>
          <path d="M290 268 C296 270.5 336 270.5 342 268" stroke="#8E211B" stroke-width="1.4" fill="none" opacity=".8"/>
          <ellipse cx="303" cy="253" rx="6" ry="2.2" transform="rotate(-18 303 253)" fill="#fff" opacity=".9"/>
          <ellipse cx="333" cy="257" rx="2.6" ry="1.2" transform="rotate(20 333 257)" fill="#fff" opacity=".8"/>
          <ellipse cx="316" cy="243.6" rx="3.4" ry="1.4" fill="url(#gBrass)"/>
        </g>''')

w('<g transform="translate(426 412) scale(.46) translate(-404 -300)">')
# pilea (Chinese money plant): round leaves on a dome, each facing outward, back leaves darker
pc = (404, 258)
dome = (404, 232); R = 44
pl = []
for el, n, ph, r in [(80, 3, 30, 11.5), (48, 7, 12, 12.5), (16, 9, 0, 13.5)]:
    for k in range(n):
        az = math.radians(ph + k * 360 / n + rnd.uniform(-8, 8))
        e_ = math.radians(el + rnd.uniform(-6, 6))
        X, Y, Z = R * math.cos(e_) * math.cos(az), R * math.sin(e_), R * math.cos(e_) * math.sin(az)
        pl.append((X, Y, Z, r * rnd.uniform(.9, 1.1)))
pl.sort(key=lambda q: q[2])
tones = ['#2B6B35', '#367F3B', '#479341', '#5EA849', '#78BC57']
rims = ['#4E9A48', '#5DAE52', '#74C25C', '#8ED36A', '#A6E07E']
svg_ = ''
for X, Y, Z, r in pl:
    x = dome[0] + X * 1.18; y = dome[1] - Y * .9 + Z * .38
    nx, ny = X / R * 1.18, (-Y / R * .9 + Z / R * .38)
    m = min(.82, math.hypot(nx, ny))
    ry = r * max(.42, math.sqrt(1 - m * m)); ang = math.degrees(math.atan2(ny, nx)) + 90
    lit = max(0, min(.999, (Z / R) * .5 + .5 + (Y / R) * .15))
    ti = int(lit * len(tones))
    ax, ay = x - nx * r * .25, y - ny * r * .25          # where the stalk meets the leaf
    svg_ += f'<path d="M{pc[0]} {pc[1]} Q{(pc[0] + ax) / 2:.1f} {min(pc[1], ay) - 8:.1f} {ax:.1f} {ay:.1f}" stroke="#6E9446" stroke-width="1.3" fill="none"/>'
    svg_ += (f'<g transform="rotate({ang:.0f} {x:.1f} {y:.1f})">'
             f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{tones[ti]}" stroke="{rims[ti]}" stroke-width="1.4"/>'
             f'<ellipse cx="{x + r * .12:.1f}" cy="{y + ry * .12:.1f}" rx="{r * .62:.1f}" ry="{ry * .6:.1f}" fill="#1E4A24" opacity=".2"/>'
             f'<path d="' + ' '.join(f'M{x:.1f} {y + ry * .18:.1f} L{x + math.cos(math.radians(v)) * r * .72:.1f} {y + ry * .18 + math.sin(math.radians(v)) * ry * .72:.1f}' for v in (-150, -115, -90, -65, -30)) +
             f'" stroke="#1E4A24" stroke-opacity=".3" stroke-width=".8"/>'
             f'<ellipse cx="{x:.1f}" cy="{y + ry * .18:.1f}" rx="1.4" ry="2.2" fill="{rims[min(4, ti + 1)]}"/></g>')
w(f'''        <g class="plant-up c-plant" style="--o:404px 266px; --t:5.8s; --dl:-1.2s">
          <path d="M402 272 C402 266 403 262 404 258 M406 272 C406 266 405 262 404 258" stroke="#7A6A3E" stroke-width="2.4" fill="none"/>
          {svg_}
        </g>
        <g class="c-sm">
          <path d="M378 272 H430 L425 300 H383Z" fill="url(#gClay)"/>
          <rect x="376" y="268" width="56" height="7" rx="3" fill="#EFD8CB"/>
          <path d="M386 280 l10 14 M398 278 l12 18 M412 279 l8 12" stroke="#F8E7DC" stroke-width="2.4" stroke-linecap="round" opacity=".8"/>
          <path d="M384 292 l14 -10 M402 298 l16 -14" stroke="#D5B09C" stroke-width="2" stroke-linecap="round" opacity=".6"/>
        </g>''')

w('</g>')

w('''
        <!-- Thank-you bouquet in a hatbox, on top of the bookshelf -->
        <g class="obj lift big" id="o-bouquet" data-id="bouquet" tabindex="0" role="button" aria-label="Bouquet: a thank-you gift">
          <g id="bq-art" transform="translate(324 300) scale(1.36) translate(-987 -584)">
          <rect x="934" y="498" width="102" height="88" fill="transparent"/>
          <g opacity=".95"><path d="M950 548 Q946.0 524.0 930 500" stroke="#4E6B57" stroke-width="1" fill="none"/><ellipse cx="943.3" cy="540.0" rx="3.6" ry="2.6" fill="#5E7F6A"/><ellipse cx="950.1" cy="538.6" rx="3.4" ry="2.4" fill="#5E7F6A" opacity=".9"/><ellipse cx="939.9" cy="532.0" rx="3.6" ry="2.6" fill="#5E7F6A"/><ellipse cx="946.7" cy="530.6" rx="3.4" ry="2.4" fill="#5E7F6A" opacity=".9"/><ellipse cx="936.6" cy="524.0" rx="3.6" ry="2.6" fill="#5E7F6A"/><ellipse cx="943.4" cy="522.6" rx="3.4" ry="2.4" fill="#5E7F6A" opacity=".9"/><ellipse cx="933.3" cy="516.0" rx="3.6" ry="2.6" fill="#5E7F6A"/><ellipse cx="940.1" cy="514.6" rx="3.4" ry="2.4" fill="#5E7F6A" opacity=".9"/><ellipse cx="929.9" cy="508.0" rx="3.6" ry="2.6" fill="#5E7F6A"/><ellipse cx="936.7" cy="506.6" rx="3.4" ry="2.4" fill="#5E7F6A" opacity=".9"/><path d="M1020 548 Q1039.0 526.0 1046 504" stroke="#4E6B57" stroke-width="1" fill="none"/><ellipse cx="1020.9" cy="540.7" rx="3.6" ry="2.6" fill="#56786A"/><ellipse cx="1027.7" cy="539.3" rx="3.4" ry="2.4" fill="#56786A" opacity=".9"/><ellipse cx="1025.3" cy="533.3" rx="3.6" ry="2.6" fill="#56786A"/><ellipse cx="1032.1" cy="531.9" rx="3.4" ry="2.4" fill="#56786A" opacity=".9"/><ellipse cx="1029.6" cy="526.0" rx="3.6" ry="2.6" fill="#56786A"/><ellipse cx="1036.4" cy="524.6" rx="3.4" ry="2.4" fill="#56786A" opacity=".9"/><ellipse cx="1033.9" cy="518.7" rx="3.6" ry="2.6" fill="#56786A"/><ellipse cx="1040.7" cy="517.3" rx="3.4" ry="2.4" fill="#56786A" opacity=".9"/><ellipse cx="1038.3" cy="511.3" rx="3.6" ry="2.6" fill="#56786A"/><ellipse cx="1045.1" cy="509.9" rx="3.4" ry="2.4" fill="#56786A" opacity=".9"/><path d="M986 546 Q995.0 520.0 992 494" stroke="#4E6B57" stroke-width="1" fill="none"/><ellipse cx="983.6" cy="537.3" rx="3.6" ry="2.6" fill="#4E7F52"/><ellipse cx="990.4" cy="535.9" rx="3.4" ry="2.4" fill="#4E7F52" opacity=".9"/><ellipse cx="984.6" cy="528.7" rx="3.6" ry="2.6" fill="#4E7F52"/><ellipse cx="991.4" cy="527.3" rx="3.4" ry="2.4" fill="#4E7F52" opacity=".9"/><ellipse cx="985.6" cy="520.0" rx="3.6" ry="2.6" fill="#4E7F52"/><ellipse cx="992.4" cy="518.6" rx="3.4" ry="2.4" fill="#4E7F52" opacity=".9"/><ellipse cx="986.6" cy="511.3" rx="3.6" ry="2.6" fill="#4E7F52"/><ellipse cx="993.4" cy="509.9" rx="3.4" ry="2.4" fill="#4E7F52" opacity=".9"/><ellipse cx="987.6" cy="502.7" rx="3.6" ry="2.6" fill="#4E7F52"/><ellipse cx="994.4" cy="501.3" rx="3.4" ry="2.4" fill="#4E7F52" opacity=".9"/><path d="M960 540 Q958.0 526.0 944 512" stroke="#4E6B57" stroke-width="1" fill="none"/><ellipse cx="953.9" cy="535.3" rx="3.6" ry="2.6" fill="#3F6E3B"/><ellipse cx="960.7" cy="533.9" rx="3.4" ry="2.4" fill="#3F6E3B" opacity=".9"/><ellipse cx="951.3" cy="530.7" rx="3.6" ry="2.6" fill="#3F6E3B"/><ellipse cx="958.1" cy="529.3" rx="3.4" ry="2.4" fill="#3F6E3B" opacity=".9"/><ellipse cx="948.6" cy="526.0" rx="3.6" ry="2.6" fill="#3F6E3B"/><ellipse cx="955.4" cy="524.6" rx="3.4" ry="2.4" fill="#3F6E3B" opacity=".9"/><ellipse cx="945.9" cy="521.3" rx="3.6" ry="2.6" fill="#3F6E3B"/><ellipse cx="952.7" cy="519.9" rx="3.4" ry="2.4" fill="#3F6E3B" opacity=".9"/><ellipse cx="943.3" cy="516.7" rx="3.6" ry="2.6" fill="#3F6E3B"/><ellipse cx="950.1" cy="515.3" rx="3.4" ry="2.4" fill="#3F6E3B" opacity=".9"/><ellipse cx="952" cy="522" rx="8" ry="3.6" transform="rotate(-40 952 522)" fill="#3F6E3B"/><ellipse cx="1022" cy="520" rx="8" ry="3.6" transform="rotate(40 1022 520)" fill="#3F6E3B"/><ellipse cx="970" cy="500" rx="8" ry="3.6" transform="rotate(-70 970 500)" fill="#4E7F42"/><ellipse cx="1008" cy="498" rx="8" ry="3.6" transform="rotate(65 1008 498)" fill="#4E7F42"/><ellipse cx="1030" cy="538" rx="8" ry="3.6" transform="rotate(20 1030 538)" fill="#5E8F4E"/></g>
          <path d="M960 540 L948 506 M954 546 L936 526" stroke="#9AAACB" stroke-width="1.1"/>
          <circle cx="958.0" cy="534.0" r="1.6" fill="#B9C7E2"/><circle cx="955.4" cy="528.5" r="1.6" fill="#B9C7E2"/><circle cx="952.8" cy="523.0" r="1.6" fill="#B9C7E2"/><circle cx="950.2" cy="517.5" r="1.6" fill="#B9C7E2"/><circle cx="947.6" cy="512.0" r="1.6" fill="#B9C7E2"/><circle cx="945.0" cy="506.5" r="1.6" fill="#B9C7E2"/><circle cx="942.4" cy="501.0" r="1.6" fill="#B9C7E2"/><circle cx="950.0" cy="544.0" r="1.6" fill="#B9C7E2"/><circle cx="947.2" cy="540.6" r="1.6" fill="#B9C7E2"/><circle cx="944.4" cy="537.2" r="1.6" fill="#B9C7E2"/><circle cx="941.6" cy="533.8" r="1.6" fill="#B9C7E2"/><circle cx="938.8" cy="530.4" r="1.6" fill="#B9C7E2"/><circle cx="936.0" cy="527.0" r="1.6" fill="#B9C7E2"/>
          <ellipse cx="958" cy="548" rx="7" ry="3" transform="rotate(-30 958 548)" fill="#5E8F4E"/><ellipse cx="1014" cy="546" rx="7" ry="3" transform="rotate(35 1014 546)" fill="#4E7F42"/><ellipse cx="996" cy="510" rx="7" ry="3" transform="rotate(-60 996 510)" fill="#6E9F5A"/><ellipse cx="968" cy="506" rx="7" ry="3" transform="rotate(50 968 506)" fill="#5E8F4E"/>
          <circle cx="1006" cy="516" r="7" fill="#7EA5DD"/><path d="M1001.1 516.0 A4.9 4.9 0 0 1 1009.5 512.5 M1009.9 516.7 A3.1 3.1 0 0 1 1004.6 518.8 M1004.2 515.3 A1.8 1.8 0 0 1 1007.0 514.6" stroke="#4D75B6" stroke-width="1.0" fill="none" stroke-linecap="round"/><circle cx="1003.9" cy="513.5" r="1.5" fill="#fff" opacity=".35"/><polygon points="1022.6,506.0 1023.2,507.8 1021.5,508.5 1020.8,510.2 1019.0,509.6 1017.2,510.2 1016.5,508.5 1014.8,507.8 1015.4,506.0 1014.8,504.2 1016.5,503.5 1017.2,501.8 1019.0,502.4 1020.8,501.8 1021.5,503.5 1023.2,504.2" fill="#82A6DB"/><circle cx="1019" cy="506" r="2.3" fill="#B0CAEE"/><g><ellipse cx="975.4" cy="512.0" rx="4" ry="3" transform="rotate(0 975.4 512.0)" fill="#25479A"/><ellipse cx="973.1" cy="515.2" rx="4" ry="3" transform="rotate(72 973.1 515.2)" fill="#25479A"/><ellipse cx="969.2" cy="514.0" rx="4" ry="3" transform="rotate(144 969.2 514.0)" fill="#25479A"/><ellipse cx="969.2" cy="510.0" rx="4" ry="3" transform="rotate(216 969.2 510.0)" fill="#25479A"/><ellipse cx="973.1" cy="508.8" rx="4" ry="3" transform="rotate(288 973.1 508.8)" fill="#25479A"/><circle cx="972" cy="512" r="1.8" fill="#C9D66A"/></g><circle cx="966.0" cy="528.0" r="5.6" fill="#9BBCE8"/><circle cx="964.5" cy="530.8" r="5.6" fill="#9BBCE8"/><circle cx="961.1" cy="531.5" r="5.6" fill="#9BBCE8"/><circle cx="958.4" cy="529.6" r="5.6" fill="#9BBCE8"/><circle cx="958.4" cy="526.4" r="5.6" fill="#9BBCE8"/><circle cx="961.1" cy="524.5" r="5.6" fill="#9BBCE8"/><circle cx="964.5" cy="525.2" r="5.6" fill="#9BBCE8"/><circle cx="962" cy="528" r="5.0" fill="#7CA0D6"/><circle cx="961" cy="527" r="2.7" fill="#BCD3F1"/><ellipse cx="986.4" cy="521.1" rx="3.6" ry="2.7" transform="rotate(17 986.4 521.1)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="983.8" cy="523.5" rx="3.6" ry="2.7" transform="rotate(77 983.8 523.5)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="980.4" cy="522.4" rx="3.6" ry="2.7" transform="rotate(137 980.4 522.4)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="979.6" cy="518.9" rx="3.6" ry="2.7" transform="rotate(197 979.6 518.9)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="982.2" cy="516.5" rx="3.6" ry="2.7" transform="rotate(257 982.2 516.5)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="985.6" cy="517.6" rx="3.6" ry="2.7" transform="rotate(317 985.6 517.6)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><circle cx="983" cy="520" r="1.9" fill="#E8D35A"/><circle cx="983" cy="520" r="0.9" fill="#5B7A3A"/><circle cx="1001" cy="532" r="7.6" fill="#6A93CF"/><path d="M995.7 532.0 A5.3 5.3 0 0 1 1004.8 528.2 M1005.2 532.8 A3.4 3.4 0 0 1 999.5 535.0 M999.1 531.2 A1.9 1.9 0 0 1 1002.1 530.5" stroke="#3F68AE" stroke-width="1.1" fill="none" stroke-linecap="round"/><circle cx="998.7" cy="529.3" r="1.7" fill="#fff" opacity=".35"/><ellipse cx="1020.2" cy="529.0" rx="3.3" ry="2.5" transform="rotate(17 1020.2 529.0)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="1017.7" cy="531.2" rx="3.3" ry="2.5" transform="rotate(77 1017.7 531.2)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="1014.6" cy="530.2" rx="3.3" ry="2.5" transform="rotate(137 1014.6 530.2)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="1013.8" cy="527.0" rx="3.3" ry="2.5" transform="rotate(197 1013.8 527.0)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="1016.3" cy="524.8" rx="3.3" ry="2.5" transform="rotate(257 1016.3 524.8)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="1019.4" cy="525.8" rx="3.3" ry="2.5" transform="rotate(317 1019.4 525.8)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><circle cx="1017" cy="528" r="1.8" fill="#E8D35A"/><circle cx="1017" cy="528" r="0.8" fill="#5B7A3A"/><circle cx="976" cy="541" r="7" fill="#8CB0E2"/><path d="M971.1 541.0 A4.9 4.9 0 0 1 979.5 537.5 M979.9 541.7 A3.1 3.1 0 0 1 974.6 543.8 M974.2 540.3 A1.8 1.8 0 0 1 977.0 539.6" stroke="#4D75B6" stroke-width="1.0" fill="none" stroke-linecap="round"/><circle cx="973.9" cy="538.5" r="1.5" fill="#fff" opacity=".35"/><ellipse cx="994.3" cy="544.0" rx="3.4" ry="2.6" transform="rotate(17 994.3 544.0)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="991.8" cy="546.3" rx="3.4" ry="2.6" transform="rotate(77 991.8 546.3)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="988.5" cy="545.3" rx="3.4" ry="2.6" transform="rotate(137 988.5 545.3)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="987.7" cy="542.0" rx="3.4" ry="2.6" transform="rotate(197 987.7 542.0)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="990.2" cy="539.7" rx="3.4" ry="2.6" transform="rotate(257 990.2 539.7)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><ellipse cx="993.5" cy="540.7" rx="3.4" ry="2.6" transform="rotate(317 993.5 540.7)" fill="#F7F9FD" stroke="#AFC1DB" stroke-width=".6"/><circle cx="991" cy="543" r="1.9" fill="#E8D35A"/><circle cx="991" cy="543" r="0.9" fill="#5B7A3A"/><polygon points="972.6,550.0 973.2,551.8 971.5,552.5 970.8,554.2 969.0,553.6 967.2,554.2 966.5,552.5 964.8,551.8 965.4,550.0 964.8,548.2 966.5,547.5 967.2,545.8 969.0,546.4 970.8,545.8 971.5,547.5 973.2,548.2" fill="#82A6DB"/><circle cx="969" cy="550" r="2.3" fill="#B0CAEE"/><polygon points="984.6,552.0 985.2,553.8 983.5,554.5 982.8,556.2 981.0,555.6 979.2,556.2 978.5,554.5 976.8,553.8 977.4,552.0 976.8,550.2 978.5,549.5 979.2,547.8 981.0,548.4 982.8,547.8 983.5,549.5 985.2,550.2" fill="#82A6DB"/><circle cx="981" cy="552" r="2.3" fill="#B0CAEE"/><polygon points="998.6,550.0 999.2,551.8 997.5,552.5 996.8,554.2 995.0,553.6 993.2,554.2 992.5,552.5 990.8,551.8 991.4,550.0 990.8,548.2 992.5,547.5 993.2,545.8 995.0,546.4 996.8,545.8 997.5,547.5 999.2,548.2" fill="#82A6DB"/><circle cx="995" cy="550" r="2.3" fill="#B0CAEE"/><ellipse cx="957.4" cy="538.0" rx="1.7" ry="0.8" transform="rotate(0 957.4 538.0)" fill="#FFFFFF"/><ellipse cx="956.7" cy="539.7" rx="1.7" ry="0.8" transform="rotate(45 956.7 539.7)" fill="#FFFFFF"/><ellipse cx="955.0" cy="540.4" rx="1.7" ry="0.8" transform="rotate(90 955.0 540.4)" fill="#FFFFFF"/><ellipse cx="953.3" cy="539.7" rx="1.7" ry="0.8" transform="rotate(135 953.3 539.7)" fill="#FFFFFF"/><ellipse cx="952.6" cy="538.0" rx="1.7" ry="0.8" transform="rotate(180 952.6 538.0)" fill="#FFFFFF"/><ellipse cx="953.3" cy="536.3" rx="1.7" ry="0.8" transform="rotate(225 953.3 536.3)" fill="#FFFFFF"/><ellipse cx="955.0" cy="535.6" rx="1.7" ry="0.8" transform="rotate(270 955.0 535.6)" fill="#FFFFFF"/><ellipse cx="956.7" cy="536.3" rx="1.7" ry="0.8" transform="rotate(315 956.7 536.3)" fill="#FFFFFF"/><circle cx="955" cy="538" r="1.1" fill="#F2C84B"/><ellipse cx="1014.4" cy="542.0" rx="1.7" ry="0.8" transform="rotate(0 1014.4 542.0)" fill="#FFFFFF"/><ellipse cx="1013.7" cy="543.7" rx="1.7" ry="0.8" transform="rotate(45 1013.7 543.7)" fill="#FFFFFF"/><ellipse cx="1012.0" cy="544.4" rx="1.7" ry="0.8" transform="rotate(90 1012.0 544.4)" fill="#FFFFFF"/><ellipse cx="1010.3" cy="543.7" rx="1.7" ry="0.8" transform="rotate(135 1010.3 543.7)" fill="#FFFFFF"/><ellipse cx="1009.6" cy="542.0" rx="1.7" ry="0.8" transform="rotate(180 1009.6 542.0)" fill="#FFFFFF"/><ellipse cx="1010.3" cy="540.3" rx="1.7" ry="0.8" transform="rotate(225 1010.3 540.3)" fill="#FFFFFF"/><ellipse cx="1012.0" cy="539.6" rx="1.7" ry="0.8" transform="rotate(270 1012.0 539.6)" fill="#FFFFFF"/><ellipse cx="1013.7" cy="540.3" rx="1.7" ry="0.8" transform="rotate(315 1013.7 540.3)" fill="#FFFFFF"/><circle cx="1012" cy="542" r="1.1" fill="#F2C84B"/><ellipse cx="1008.2" cy="521.0" rx="1.5" ry="0.8" transform="rotate(0 1008.2 521.0)" fill="#FFFFFF"/><ellipse cx="1007.6" cy="522.6" rx="1.5" ry="0.8" transform="rotate(45 1007.6 522.6)" fill="#FFFFFF"/><ellipse cx="1006.0" cy="523.2" rx="1.5" ry="0.8" transform="rotate(90 1006.0 523.2)" fill="#FFFFFF"/><ellipse cx="1004.4" cy="522.6" rx="1.5" ry="0.8" transform="rotate(135 1004.4 522.6)" fill="#FFFFFF"/><ellipse cx="1003.8" cy="521.0" rx="1.5" ry="0.8" transform="rotate(180 1003.8 521.0)" fill="#FFFFFF"/><ellipse cx="1004.4" cy="519.4" rx="1.5" ry="0.8" transform="rotate(225 1004.4 519.4)" fill="#FFFFFF"/><ellipse cx="1006.0" cy="518.8" rx="1.5" ry="0.8" transform="rotate(270 1006.0 518.8)" fill="#FFFFFF"/><ellipse cx="1007.6" cy="519.4" rx="1.5" ry="0.8" transform="rotate(315 1007.6 519.4)" fill="#FFFFFF"/><circle cx="1006" cy="521" r="1.0" fill="#F2C84B"/><ellipse cx="967.2" cy="519.0" rx="1.5" ry="0.8" transform="rotate(0 967.2 519.0)" fill="#FFFFFF"/><ellipse cx="966.6" cy="520.6" rx="1.5" ry="0.8" transform="rotate(45 966.6 520.6)" fill="#FFFFFF"/><ellipse cx="965.0" cy="521.2" rx="1.5" ry="0.8" transform="rotate(90 965.0 521.2)" fill="#FFFFFF"/><ellipse cx="963.4" cy="520.6" rx="1.5" ry="0.8" transform="rotate(135 963.4 520.6)" fill="#FFFFFF"/><ellipse cx="962.8" cy="519.0" rx="1.5" ry="0.8" transform="rotate(180 962.8 519.0)" fill="#FFFFFF"/><ellipse cx="963.4" cy="517.4" rx="1.5" ry="0.8" transform="rotate(225 963.4 517.4)" fill="#FFFFFF"/><ellipse cx="965.0" cy="516.8" rx="1.5" ry="0.8" transform="rotate(270 965.0 516.8)" fill="#FFFFFF"/><ellipse cx="966.6" cy="517.4" rx="1.5" ry="0.8" transform="rotate(315 966.6 517.4)" fill="#FFFFFF"/><circle cx="965" cy="519" r="1.0" fill="#F2C84B"/><ellipse cx="990.0" cy="532.0" rx="1.4" ry="0.7" transform="rotate(0 990.0 532.0)" fill="#FFFFFF"/><ellipse cx="989.4" cy="533.4" rx="1.4" ry="0.7" transform="rotate(45 989.4 533.4)" fill="#FFFFFF"/><ellipse cx="988.0" cy="534.0" rx="1.4" ry="0.7" transform="rotate(90 988.0 534.0)" fill="#FFFFFF"/><ellipse cx="986.6" cy="533.4" rx="1.4" ry="0.7" transform="rotate(135 986.6 533.4)" fill="#FFFFFF"/><ellipse cx="986.0" cy="532.0" rx="1.4" ry="0.7" transform="rotate(180 986.0 532.0)" fill="#FFFFFF"/><ellipse cx="986.6" cy="530.6" rx="1.4" ry="0.7" transform="rotate(225 986.6 530.6)" fill="#FFFFFF"/><ellipse cx="988.0" cy="530.0" rx="1.4" ry="0.7" transform="rotate(270 988.0 530.0)" fill="#FFFFFF"/><ellipse cx="989.4" cy="530.6" rx="1.4" ry="0.7" transform="rotate(315 989.4 530.6)" fill="#FFFFFF"/><circle cx="988" cy="532" r="0.9" fill="#F2C84B"/>
          <path d="M1020 548 L1026 530" stroke="#C9A04A" stroke-width="1"/>
          <g transform="rotate(-12 1030 528)">
            <rect x="1018" y="518" width="24" height="16" rx="1.5" fill="#EEF3FB"/>
            <path d="M1022 523 H1038 M1022 526.5 H1036 M1022 530 H1033" stroke="#8FA8CE" stroke-width=".8"/>
          </g>
          <path d="M970 552 H1004 V580 Q1004 584 998 584 H976 Q970 584 970 580Z" fill="url(#gHatboxBlue)"/>
          <rect x="969" y="551" width="36" height="6" rx="2" fill="#E4ECF6"/>
          <rect x="969" y="556" width="36" height="1.4" fill="#000" opacity=".06"/>
          <path d="M971 577 H1003" stroke="#9FB3CE" stroke-width="1"/>
          <path d="M987 559 L979 576 M987 559 L993 578 M987 559 L998 572" stroke="#4E7FBE" stroke-width="1.8" stroke-linecap="round"/>
          <ellipse cx="981" cy="557" rx="6" ry="3.2" transform="rotate(-20 981 557)" fill="none" stroke="#5B8BC8" stroke-width="2.4"/>
          <ellipse cx="993" cy="557" rx="6" ry="3.2" transform="rotate(20 993 557)" fill="none" stroke="#5B8BC8" stroke-width="2.4"/>
          <circle cx="987" cy="558" r="2" fill="#3F6FB0"/>
          </g>
        </g>

''')

# --- row 1 left: books (About)
books = [(166, 16, 78, '#8BA6E2', ''), (183, 14, 84, '#EFA2B5', ''), (198, 20, 72, '#A3CB8B', 'ABOUT'), (219, 13, 80, '#F4D772', ''), (233, 17, 76, '#BEB2F0', ''), (251, 15, 70, '#EDAE78', '')]
s = ''.join(book(x, 412, wd, h, c, lab) for x, wd, h, c, lab in books)
s += book(268, 412, 15, 74, '#A9C49B', '', 13, (283, 412))
w(f'''
        <g class="obj lift" id="o-books" data-id="books" tabindex="0" role="link" aria-label="Books: go to the About page">
          <rect x="164" y="326" width="130" height="86" fill="transparent"/>
          {s}
        </g>''')
# --- row 1 right: diploma + cactus
w('''        <g class="obj lift" id="o-diploma" data-id="diploma" tabindex="0" role="button" aria-label="Framed certificate: where I studied">
          <rect x="316" y="352" width="76" height="60" rx="1.5" fill="#1E1F23"/>
          <rect x="316" y="352" width="76" height=".9" fill="#5A5C63"/>
          <rect x="318.4" y="354.4" width="71.2" height="55.2" fill="#F8E3C4"/>
          <path d="M318.4 354.4 H389.59999999999997 M318.4 354.4 V409.59999999999997" stroke="#000" stroke-width="1.2" opacity=".14"/>
          <path d="M326.4 358.79999999999995 H381.59999999999997 A3.6 3.6 0 0 0 385.2 362.4 V401.59999999999997 A3.6 3.6 0 0 0 381.59999999999997 405.2 H326.4 A3.6 3.6 0 0 0 322.79999999999995 401.59999999999997 V362.4 A3.6 3.6 0 0 0 326.4 358.79999999999995Z" fill="none" stroke="#D98C4A" stroke-width="1.5"/>
          <rect x="343.0" y="363.4" width="22" height="5.8" rx="2" fill="#C97F55"/>
          <path d="M332.4 374.4 H375.59999999999997 M332.4 378.9 H375.59999999999997" stroke="#E3B48E" stroke-width="1.7" stroke-linecap="round"/>
          <path d="M364.4 389.4 c1.4 -2.8 2.8 -2.8 1.9 0 c-.9 2.8 .9 2.8 2.4 -.6 c.9 -2.2 2 -1.8 1.5 .4 c-.4 1.5 1.1 1.3 2.2 -.4" stroke="#9E4A2C" stroke-width=".85" fill="none" stroke-linecap="round"/>
          <path d="M350.4 399.59999999999997 L348.0 407.59999999999997 L350.0 406.2 L351.2 407.99999999999994 L353.2 400.59999999999997Z" fill="#D9343A"/>
          <path d="M354.0 400.59999999999997 L355.6 407.99999999999994 L357.0 406.2 L358.8 407.59999999999997 L356.4 399.59999999999997Z" fill="#B82830"/>
          <polygon points="358.8,397.6 357.8,398.9 358.0,400.5 356.5,401.1 355.9,402.6 354.3,402.4 353.0,403.4 351.7,402.4 350.1,402.6 349.5,401.1 348.0,400.5 348.2,398.9 347.2,397.6 348.2,396.3 348.0,394.7 349.5,394.1 350.1,392.6 351.7,392.8 353.0,391.8 354.3,392.8 355.9,392.6 356.5,394.1 358.0,394.7 357.8,396.3" fill="#F4B03A"/>
          <circle cx="353.0" cy="397.59999999999997" r="3.9" fill="#F7A42C" stroke="#B9702A" stroke-width=".9"/>
          <circle cx="352.1" cy="396.7" r="1.4" fill="#FFD27A" opacity=".8"/>
          <path d="M320.4 372.4 L336.4 356.4 H342.4 L320.4 378.4Z" fill="#fff" opacity=".14"/>
        </g>''')

# --- row 2 left: record player
w('''
        <g class="obj lift" id="o-record" data-id="record" tabindex="0" role="button" aria-label="Record player: on repeat">
          <!-- smoked acrylic lid, standing open -->
          <path d="M172 486 V440 Q172 437 175 437 H285 Q288 437 288 440 V486Z" fill="#5C4632" opacity=".34"/>
          <path d="M172 486 V440 Q172 437 175 437 H285 Q288 437 288 440 V486" stroke="#3E2E20" stroke-width="1.2" fill="none" opacity=".55"/>
          <rect x="174" y="439" width="112" height="3" rx="1.5" fill="#3E2E20" opacity=".35"/>
          <path d="M178 474 L190 446 H197 L185 476Z" fill="#FFFFFF" opacity=".16"/>
          <rect x="225" y="455" width="10" height="6" rx="1" fill="#B59A6A" opacity=".7"/>
          <rect x="172" y="483" width="5" height="4" rx="1" fill="#1E1F23"/><rect x="283" y="483" width="5" height="4" rx="1" fill="#1E1F23"/>
          <!-- walnut top deck -->
          <path d="M170 485.4 H288 L293 492 H165Z" fill="#7A4E31"/>
          <path d="M170 485.4 H288" stroke="#A97650" stroke-width=".8"/>
          <!-- platter: a solid cylinder -->
          <path d="M176.5 488.6 V492.0 A35.5 5.50 0 0 0 247.5 492.0 V488.6Z" fill="url(#gPlatterSide)"/>
          <path d="M178.5 492.0 A33.5 5.20 0 0 0 245.5 492.0" stroke="#5A5E68" stroke-width=".6" fill="none" opacity=".8"/>
          <ellipse cx="212" cy="488.6" rx="35.5" ry="5.50" fill="#17181C"/>
          <!-- the record: a thin disc with its own edge; its top turns when playing -->
          <path d="M178 487.0 V488.3 A34 5.27 0 0 0 246 488.3 V487.0Z" fill="#0B0C0F"/>
          <path d="M179 488.2 A33 5.07 0 0 0 245 488.2" stroke="#3E414A" stroke-width=".5" fill="none"/>
          <g transform="translate(212 487.0) scale(1 0.155)">
            <circle r="34" fill="#1C1E24"/>
            <circle r="29" fill="none" stroke="#33363E" stroke-width="1"/>
            <circle r="23" fill="none" stroke="#33363E" stroke-width="1"/>
            <circle r="17" fill="none" stroke="#33363E" stroke-width="1"/>
            <g class="disc-spin">
              <path d="M-27 -13 A30 30 0 0 1 -6 -29.5 M20 20 A29 29 0 0 1 4 28.6" stroke="#5A5E68" stroke-width="2.2" fill="none"/>
              <circle r="11" fill="#F3E6D3"/>
              <rect x="-7.6" y="-2.3" width="15.2" height="4.6" rx="1" fill="#C0553E"/>
              <path d="M-5.6 -6.2 h11.2 M-4.8 6.2 h9.6" stroke="#8A6A4A" stroke-width="1.2"/>
              <circle cx="0" cy="-8.6" r="1.3" fill="#C0553E"/>
            </g>
            <path d="M8 -34 A34 34 0 0 1 32 -11 L11 -4 A11 11 0 0 0 4 -10.6Z" fill="#FFFFFF" opacity=".1"/>
          </g>
          <rect x="211.4" y="484.4" width="1.2" height="2.8" rx=".4" fill="#C9CDD3"/>
          <!-- tonearm, counterweight and knobs on the right -->
          <ellipse cx="274" cy="487.6" rx="4.2" ry="1.6" fill="#24262C"/>
          <rect x="272.6" y="483.6" width="2.8" height="4" fill="#2E3036"/>
          <rect x="276" y="482.6" width="6" height="3.4" rx="1.2" fill="#1A1B1F"/>
          <path d="M274 484 L246 487.6" stroke="url(#gChrome)" stroke-width="1.5" stroke-linecap="round"/>
          <path d="M242.6 486.4 L248.6 485.8 L249 489 L243 489.6Z" fill="#1A1B1F"/>
          <rect x="243.6" y="488.2" width="3.4" height="1.4" fill="#C9CDD3"/>
          <g fill="#1A1B1F"><ellipse cx="280" cy="490" rx="2.2" ry="1"/><ellipse cx="285" cy="490" rx="2.2" ry="1"/><ellipse cx="290" cy="490" rx="2" ry=".9"/></g>
          <g fill="#2E3036"><rect x="277.8" y="488.2" width="4.4" height="1.8" rx=".8"/><rect x="282.8" y="488.2" width="4.4" height="1.8" rx=".8"/><rect x="288" y="488.4" width="4" height="1.6" rx=".8"/></g>
          <!-- walnut case with a black fabric front and thin gold trim -->
          <rect x="165" y="492" width="128" height="24" rx="2" fill="url(#gWalnutCase)"/>
          <rect x="165" y="492" width="128" height="1.2" fill="#B58358" opacity=".8"/>
          <rect x="170" y="495.4" width="118" height="17.2" rx="1.2" fill="#2A2B30"/>
          <rect x="170" y="495.4" width="118" height="17.2" rx="1.2" fill="url(#gShadeV)" opacity=".5"/>
          <rect x="170.6" y="496" width="116.8" height="16" rx="1" fill="none" stroke="#C9A25A" stroke-width=".7"/>
          <path d="M224 504.6 c2 -2.2 4 -2.2 5 0 c1 2 3 2 4 0 c1 -2 3 -2 4.4 .2" stroke="#C9A25A" stroke-width=".6" fill="none" stroke-linecap="round" opacity=".85"/>
          <rect x="171" y="516" width="8" height="2" rx="1" fill="#1A1B1F"/><rect x="279" y="516" width="8" height="2" rx="1" fill="#1A1B1F"/>
          <g class="notes" fill="#3A57C4"><text x="196" y="470" class="svg-note">♪</text><text x="226" y="458" class="svg-note n2">♫</text></g>
        </g>''')
# --- row 2 right: trophy + stacked books
w('''        <!-- Crystal award on a round LED base: click to switch the RGB light on (the crystal turns) -->
        <g class="obj lift award" id="o-trophy" data-id="trophy" tabindex="0" role="button" aria-label="Crystal award: kind words">
          <ellipse class="award-glow" cx="350" cy="497" rx="34" ry="14" fill="currentColor" filter="url(#soft)"/>
          <!-- the crystal is a real 4-sided block; script.js recomputes the faces as it turns -->
          <g id="crystal3d">
            <polygon class="cf" points="339.7,450.4 334.8,452.0 334.8,502.0 339.7,500.4" fill="#c1d3e0" fill-opacity="0.3" stroke="#FFFFFF" stroke-width=".7" stroke-opacity="0.25"/>
            <polygon class="cf" points="365.2,452.0 339.7,450.4 339.7,500.4 365.2,502.0" fill="#c1d3e0" fill-opacity="0.3" stroke="#FFFFFF" stroke-width=".7" stroke-opacity="0.25"/>
            <g id="award-etch" transform="translate(350 0) scale(0.913 1) translate(-350 0)">
              <g stroke="#FFFFFF" stroke-linecap="round" opacity=".95">
                <path d="M342 473 h16" stroke-width="1"/>
                <path d="M342 478 L359 482" stroke-width="1.6"/>
                <path d="M343 488 h10 M341 491.5 h15 M342 494.5 h13 M345 498 h8" stroke-width=".9"/>
              </g>
              <!-- engraving: AWARD + thumbs-up, white with a crisp outline -->
              <text x="344.6" y="464.4" text-anchor="middle" class="svg-etch" stroke="#4E6A80" stroke-width=".55" paint-order="stroke" stroke-linejoin="round">AWARD</text>
              <g transform="translate(356.4 457) scale(1.2)">
                <path d="M0 3.2 h1.6 v4.6 h-1.6Z M2.2 3.4 c1 -.6 1.6 -1.8 1.8 -3 c.1 -.6 1.1 -.6 1.2 .2 c.1 .9 -.2 1.8 -.5 2.5 h2.2 c.8 0 1.2 .8 .9 1.3 c.5 .3 .4 1.1 -.1 1.3 c.4 .4 .2 1.1 -.3 1.2 c.2 .5 -.2 1 -.8 1 h-4.4Z" fill="#FFFFFF" stroke="#4E6A80" stroke-width=".45" stroke-linejoin="round" paint-order="stroke"/>
              </g>
            </g>
            <polygon class="cf" points="334.8,452.0 360.3,453.6 360.3,503.6 334.8,502.0" fill="#f6fafe" fill-opacity="0.62" stroke="#FFFFFF" stroke-width=".7" stroke-opacity="0.9"/>
            <polygon class="cf" points="360.3,453.6 365.2,452.0 365.2,502.0 360.3,503.6" fill="#cbdae5" fill-opacity="0.62" stroke="#FFFFFF" stroke-width=".7" stroke-opacity="0.9"/>
            <polygon id="award-top" points="339.7,450.4 365.2,452.0 360.3,453.6 334.8,452.0" fill="#FFFFFF" fill-opacity=".75"/>
            <polygon id="award-tint" class="award-tint" points="334.8,452 365.2,452 365.2,502 334.8,502" fill="currentColor" opacity="0"/>
          </g>
          <path d="M326 503 V514 Q326 518 332 518 H368 Q374 518 374 514 V503Z" fill="url(#gAlu)"/>
          <ellipse cx="350" cy="503" rx="24" ry="4.2" fill="#DDE7EE"/>
          <ellipse class="award-led" cx="350" cy="503" rx="23" ry="3.8" fill="none" stroke="#B8BEC6" stroke-width="1.4"/>
          <ellipse cx="350" cy="503" rx="19" ry="2.8" fill="#F4F8FB" opacity=".8"/>
          <rect x="341" y="512" width="6" height="5" rx="1" fill="#24272E"/><rect x="353" y="512" width="6" height="5" rx="1" fill="#24272E"/>
        </g>
        <g class="c-sm">''' + flatbook(388, 518, 60, 15, '#8BA6E2') + flatbook(392, 503, 54, 13, '#F4D772') + flatbook(386, 490, 58, 12, '#A3CB8B') + '</g>')

# --- row 3 left: purple shamrock (oxalis) in a round stone pot + stacked books
OX_LEAFLET = 'M0 0 C-3 -4 -9 -10 -12 -15 C-9 -19.5 -3 -19.5 0 -14 C3 -19.5 9 -19.5 12 -15 C9 -10 3 -4 0 0Z'
OX_STRIPE = 'M0 -1.5 C-2 -5 -5 -10 -6.5 -14 C-3.5 -15.5 -1 -14.5 0 -11.5 C1 -14.5 3.5 -15.5 6.5 -14 C5 -10 2 -5 0 -1.5Z'
def oxa(cx, cy, sc, rot, tilt=.74):
    g = f'<g transform="translate({cx} {cy}) rotate({rot}) scale({sc} {sc * tilt:.2f})">'
    for a in (0, 120, 240):
        g += f'<g transform="rotate({a})"><path d="{OX_LEAFLET}" fill="url(#gOxa)"/><path d="{OX_STRIPE}" fill="#A3348C" opacity=".82"/></g>'
    return g + '<circle r="1.2" fill="#3A1433"/></g>'
def oflower(x, y, r):
    s_ = ''.join(f'<ellipse cx="{x:.1f}" cy="{y - r * .9:.1f}" rx="{r * .62:.1f}" ry="{r:.1f}" transform="rotate({a} {x:.1f} {y:.1f})" fill="#F3CBE8"/>' for a in range(0, 360, 72))
    return s_ + f'<circle cx="{x}" cy="{y}" r="{r * .35:.1f}" fill="#D3E58C"/>'
ox_leaves = [(178, 566, 1.15, 8), (207, 556, 1.25, -10), (195, 579, .95, 20), (213, 588, .82, -28), (174, 592, .78, 14)]
stems = ''.join(f'<path d="M191 606 Q{(191 + x) / 2 + (4 if x > 191 else -4):.0f} {(606 + y) / 2:.0f} {x} {y}" stroke="#7A2E5C" stroke-width="1.5" fill="none"/>' for x, y, _, _ in ox_leaves)
w(f'''        <g class="plant-up c-plant" style="--o:191px 606px; --t:5.2s; --dl:-.8s">
          {stems}
          {''.join(oxa(x, y, sc, r) for x, y, sc, r in ox_leaves)}
          <path d="M187 606 C184 590 176 566 166 548" stroke="#8CAE5A" stroke-width="1.2" fill="none"/>
          <path d="M167 550 L173 545 M167 550 L161 547" stroke="#8CAE5A" stroke-width=".9"/>
          {oflower(166, 546, 3.8)}{oflower(174, 543, 3.4)}{oflower(160, 548, 3.1)}
        </g>
        <g class="c-sm">
          <path d="M168 606 H214 C224 612 223 627 210 632 H172 C159 627 158 612 168 606Z" fill="url(#gStone)"/>
          <ellipse cx="191" cy="606" rx="23" ry="3.4" fill="#26282C"/>
          <ellipse cx="191" cy="606.6" rx="19" ry="2.3" fill="#3A2E26"/>
          <g fill="#ECE6DA"><circle cx="184" cy="606.4" r=".8"/><circle cx="197" cy="607" r=".7"/><circle cx="201" cy="606" r=".6"/></g>
          <path d="M165 614 C166 622 170 628 176 630" stroke="#82878F" stroke-width="2" fill="none" stroke-linecap="round" opacity=".6"/>
        </g>''')
w('''
        <g class="c-sm">''' + flatbook(224, 630, 70, 16, '#EFA2B5') + flatbook(228, 614, 62, 14, '#FFFDF7') + '</g>')
# --- row 3 right: books + photo frame
s = ''.join(book(x, 630, wd, h, c) for x, wd, h, c in [(318, 15, 74, '#A3CB8B'), (334, 13, 82, '#F4EEE2'), (348, 17, 70, '#8BA6E2'), (366, 12, 78, '#E58C8C'), (379, 15, 66, '#BEB2F0'), (395, 13, 74, '#F4D772')])
w(f'''        <g class="c-sm">{s}</g>
        <g class="c-sm" transform="rotate(-4 432 630)">
          <rect x="414" y="588" width="34" height="42" rx="2" fill="#FFFFFF"/>
          <rect x="419" y="593" width="24" height="30" fill="#CFE0F3"/>
          <circle cx="431" cy="604" r="5" fill="#F4D772"/>
          <path d="M419 623 L428 612 L435 618 L443 608 V623Z" fill="#A9C49B"/>
        </g>''')
# --- row 4 (bottom): books on the left, a little glow-in-the-dark figure collection on the right
s4 = ''.join(book(x, 746, wd, h, c) for x, wd, h, c in [(166, 15, 76, '#E58C8C'), (182, 13, 84, '#F4EEE2'), (196, 17, 72, '#8BA6E2'), (214, 12, 80, '#A3CB8B'), (227, 16, 70, '#F4D772'), (244, 14, 78, '#BEB2F0')])
s4 += book(259, 746, 14, 72, '#EDAE78', '', 12, (273, 746))
w(f'        <g class="c-sm">{s4}</g>')
w('        <g class="c-sm">' + flatbook(276, 746, 22, 12, '#8BA6E2') + '</g>')

def fig(x, y, pose, sc=1.0):
    """A small chubby glow-in-the-dark figure, feet at (x, y)."""
    B, L, E = 'url(#gFig)', '#E9F7CF', '#2F3A2A'
    if pose == 'hug':      # sitting, hugging knees
        parts = (f'<ellipse cx="0" cy="-6" rx="6" ry="6.4" fill="{B}"/><ellipse cx="2.4" cy="-7" rx="4.4" ry="4" fill="{L}" opacity=".7"/>'
                 f'<path d="M-3 -8 C0 -5 4 -5 6 -8" stroke="#A9CF83" stroke-width="1.2" fill="none"/>'
                 f'<ellipse cx="0" cy="-16.5" rx="6.4" ry="6" fill="{B}"/>'
                 f'<circle cx="-2" cy="-16.5" r=".6" fill="{E}"/><circle cx="1.8" cy="-16.5" r=".6" fill="{E}"/>')
    elif pose == 'cheeks': # standing, hands on cheeks
        parts = (f'<rect x="-3.2" y="-6" width="2.6" height="6" rx="1.3" fill="{B}"/><rect x=".6" y="-6" width="2.6" height="6" rx="1.3" fill="{B}"/>'
                 f'<ellipse cx="0" cy="-10" rx="5" ry="5.6" fill="{B}"/>'
                 f'<ellipse cx="0" cy="-20" rx="6.4" ry="6" fill="{B}"/>'
                 f'<circle cx="-5.6" cy="-18.6" r="1.9" fill="{L}"/><circle cx="5.6" cy="-18.6" r="1.9" fill="{L}"/>'
                 f'<circle cx="-2" cy="-20.4" r=".6" fill="{E}"/><circle cx="1.8" cy="-20.4" r=".6" fill="{E}"/>'
                 f'<ellipse cx="0" cy="-18" rx=".9" ry=".6" fill="#E9A6A0"/>')
    elif pose == 'lie':    # lying on the tummy, feet up
        parts = (f'<ellipse cx="1" cy="-3.2" rx="9" ry="3.4" fill="{B}"/>'
                 f'<ellipse cx="9" cy="-6.4" rx="1.8" ry="2.6" transform="rotate(-25 9 -6.4)" fill="{B}"/>'
                 f'<ellipse cx="-7" cy="-8" rx="5.6" ry="5.2" fill="{B}"/>'
                 f'<circle cx="-9" cy="-8.4" r=".6" fill="{E}"/><circle cx="-5.6" cy="-8.4" r=".6" fill="{E}"/>'
                 f'<circle cx="-11" cy="-3.6" r="1.6" fill="{L}"/>')
    elif pose == 'lean':   # sitting back, legs out
        parts = (f'<ellipse cx="5" cy="-2.2" rx="5.2" ry="2.2" fill="{B}"/>'
                 f'<ellipse cx="-.6" cy="-7" rx="5" ry="6" fill="{B}"/>'
                 f'<ellipse cx="-5" cy="-3" rx="1.8" ry="2.6" fill="{L}"/>'
                 f'<ellipse cx="-1.2" cy="-17" rx="6.2" ry="5.8" transform="rotate(-10 -1.2 -17)" fill="{B}"/>'
                 f'<circle cx="-3.2" cy="-17.6" r=".6" fill="{E}"/><circle cx=".6" cy="-18.2" r=".6" fill="{E}"/>')
    else:                  # cheer: arms up
        parts = (f'<rect x="-3.2" y="-6" width="2.6" height="6" rx="1.3" fill="{B}"/><rect x=".6" y="-6" width="2.6" height="6" rx="1.3" fill="{B}"/>'
                 f'<ellipse cx="0" cy="-10" rx="5" ry="5.6" fill="{B}"/>'
                 f'<ellipse cx="-5.4" cy="-15" rx="1.6" ry="3" transform="rotate(-25 -5.4 -15)" fill="{B}"/><ellipse cx="5.4" cy="-15" rx="1.6" ry="3" transform="rotate(25 5.4 -15)" fill="{B}"/>'
                 f'<ellipse cx="0" cy="-20" rx="6.4" ry="6" fill="{B}"/>'
                 f'<circle cx="-2" cy="-20" r=".6" fill="{E}"/><circle cx="1.8" cy="-20" r=".6" fill="{E}"/>'
                 f'<path d="M-1 -18 Q0 -17 1 -18" stroke="{E}" stroke-width=".5" fill="none"/>')
    return f'<g transform="translate({x} {y}) scale({sc})">{parts}</g>'

figs = (fig(326, 745, 'hug', 1.15) + fig(346, 745, 'cheeks', 1.1) + fig(374, 745, 'lie', 1.1) +
        fig(404, 724, 'lean', 1.05) + fig(432, 706, 'cheer', 1.05))
w(f'''        <g class="c-sm">
          <rect x="392" y="722" width="56" height="23" rx="1.5" fill="#F7F5F0"/>
          <rect x="392" y="722" width="56" height="2" fill="#FFFFFF"/>
          <rect x="418" y="704" width="30" height="18" rx="1.5" fill="#EFECE5"/>
          <rect x="418" y="704" width="30" height="2" fill="#FFFFFF"/>
        </g>
        <g id="figs" class="c-sm">{figs}</g>''')

w('</g>')
# ------------------------------------------------------------------ guitar
w('<g transform="translate(8 26)">')
frets = ' '.join(f'M506 {y} H518' for y in range(470, 612, 16))
w(f'''
        <!-- Guitar -->
        <g class="obj lift" id="o-guitar" data-id="guitar" tabindex="0" role="button" aria-label="Guitar: after hours">
          <g transform="rotate(5 512 766)">
            <path d="M503 420 H521 L523 452 H501Z" fill="#6B432A"/>
            <g fill="#E9E4DA"><circle cx="499" cy="428" r="2.6"/><circle cx="499" cy="438" r="2.6"/><circle cx="525" cy="428" r="2.6"/><circle cx="525" cy="438" r="2.6"/></g>
            <rect x="505" y="450" width="14" height="172" fill="url(#gNeck)"/>
            <path d="{frets}" stroke="#E4D7C0" stroke-width="1" opacity=".8"/>
            <path d="M512 612 C536 612 546 630 544 650 C542 664 534 672 534 680 C534 690 554 698 554 722 C554 748 536 766 512 766 C488 766 470 748 470 722 C470 698 490 690 490 680 C490 672 482 664 480 650 C478 630 488 612 512 612Z" fill="url(#gGuitar)"/>
            <path d="M512 612 C536 612 546 630 544 650 C542 664 534 672 534 680 C534 690 554 698 554 722 C554 748 536 766 512 766 C488 766 470 748 470 722 C470 698 490 690 490 680 C490 672 482 664 480 650 C478 630 488 612 512 612Z" fill="none" stroke="#FFF1DC" stroke-width="2" opacity=".7"/>
            <circle cx="512" cy="676" r="13" fill="none" stroke="#B9773F" stroke-width="3"/>
            <circle cx="512" cy="676" r="10" fill="#3F2717"/>
            <rect x="498" y="728" width="28" height="7" rx="2.5" fill="#5A3A26"/>
            <path d="M509 430 V732 M512 430 V732 M515 430 V732" stroke="#FFFDF5" stroke-opacity=".75" stroke-width=".7"/>
          </g>
        </g>''')

w('</g>')
# ------------------------------------------------------------------ waste basket
def smooth(pts):
    """A closed, rounded path through points (quadratic curves between their midpoints)."""
    mid = [((x0 + x1) / 2, (y0 + y1) / 2) for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])]
    d = f'M{mid[-1][0]:.1f} {mid[-1][1]:.1f}'
    for (px, py), (mx, my) in zip(pts, mid):
        d += f' Q{px:.1f} {py:.1f} {mx:.1f} {my:.1f}'
    return d + 'Z'


def crumple(x, y, r, seed):
    """A crumpled ball of paper: a lumpy round outline, a shaded underside and a few creases."""
    rr = random.Random(seed)
    pts = [(x + r * rr.uniform(.86, 1.06) * math.cos(2 * math.pi * k / 11), y + r * .92 * rr.uniform(.86, 1.06) * math.sin(2 * math.pi * k / 11)) for k in range(11)]
    creases = ' '.join(f'M{x + rr.uniform(-.55, .45) * r:.1f} {y + rr.uniform(-.55, .35) * r:.1f} l{rr.uniform(.2, .5) * r:.1f} {rr.uniform(-.3, .3) * r:.1f} l{rr.uniform(-.1, .3) * r:.1f} {rr.uniform(.15, .4) * r:.1f}' for _ in range(3))
    return (f'<path d="{smooth(pts)}" fill="#D8D0C0"/>'  # the shaded side shows round the lower right
            f'<path d="{smooth([(px - r * .12, py - r * .14) for px, py in pts])}" fill="#FBF8F1"/>'
            f'<path d="{creases}" stroke="#C4BAA6" stroke-width=".55" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def basket_cuff(cx, top, tw):
    """The gingham cuff folded over the front of the rim, with a softly scalloped hem."""
    left, right, n = cx - tw - 1.8, cx + tw + 1.8, 8
    span = right - left - 2.4
    sag = lambda x: 3.2 * (1 - (x - cx) ** 2 / (tw + 2) ** 2)   # the hem follows the curve of the rim
    xs = [left + 1.2 + span * i / n for i in range(n + 1)]
    # front half of the rim (left to right), down the right side, then the hem back to the left
    d = f'M{left:.1f} {top} A{tw + 1.8} 5.8 0 0 0 {right:.1f} {top} L{xs[-1]:.1f} {top + 9.5 + sag(xs[-1]) * .6:.1f}'
    for i in reversed(range(n)):
        xm = (xs[i] + xs[i + 1]) / 2
        d += f' Q{xm:.1f} {top + 11.5 + sag(xm) + (1.2 if i % 2 else 0):.1f} {xs[i]:.1f} {top + 9.5 + sag(xs[i]) * .6:.1f}'
    d += 'Z'
    return (f'<path d="{d}" fill="url(#gLiner)"/>'
            f'<path d="{d}" fill="url(#ginghamSm)" opacity=".75"/>'
            f'<path d="{d}" fill="url(#gCylShade)"/>'
            f'<path d="M{left:.1f} {top} A{tw + 1.8} 5.8 0 0 0 {right:.1f} {top}" stroke="#FFFFFF" stroke-width=".9" fill="none" opacity=".7"/>'
            f'<path d="M{cx - 11} {top + 5.4} l1.6 5 M{cx + 8} {top + 5.6} l-1.4 5.2" stroke="#4E6F92" stroke-width=".7" opacity=".35" stroke-linecap="round"/>')


def waste_basket():
    """A woven rattan basket with a gingham liner folded over the rim, crumpled notes inside
    and one that missed, on the floor."""
    cx, top, bot, tw, bw = 654, 727, 772, 29, 22   # centre, rim, base, half-widths at the rim and the base
    hw = lambda y: tw + (bw - tw) * (y - top) / (bot - top)
    # the body's top edge is the front of the rim, so the opening shows behind it
    body = (f'M{cx - tw} {top} L{cx - bw - .6:.1f} {bot - 4} Q{cx - bw} {bot} {cx - bw + 4} {bot} '
            f'H{cx + bw - 4} Q{cx + bw} {bot} {cx + bw + .6:.1f} {bot - 4} L{cx + tw} {top} A{tw} 5.4 0 0 1 {cx - tw} {top}Z')
    # basket weave: rows of short rounded strands, each row offset from the last, over darker gaps
    strands, shine = [], []
    for j, y in enumerate(range(top + 8, bot - 3, 4)):
        h, off = hw(y), (3.6 if j % 2 else 0)
        strands.append(f'<path d="M{cx - h - 2:.1f} {y} H{cx + h + 2:.1f}" stroke-dashoffset="{off}"/>')
        shine.append(f'<path d="M{cx - h - 2:.1f} {y - 1} H{cx + h + 2:.1f}" stroke-dashoffset="{off}"/>')
    inside = (crumple(cx - 8, top - 3.5, 5.4, 3)
              # a torn notebook page sticking up, ruled in blue, with its corner folded
              + f'<path d="M{cx + 1} {top - 1} L{cx + 5} {top - 14} L{cx + 14} {top - 9} L{cx + 12} {top - 1}Z" fill="#FFFDF7"/>'
              + f'<path d="M{cx + 5} {top - 14} L{cx + 14} {top - 9} L{cx + 12} {top - 7.6}Z" fill="#E6DFD0"/>'
              + f'<path d="M{cx + 3.8} {top - 9.4} L{cx + 11.6} {top - 5.6} M{cx + 2.8} {top - 5.4} L{cx + 10.8} {top - 1.8}" stroke="#9DB4E8" stroke-width=".7"/>'
              + crumple(cx + 9, top - 2.4, 4.4, 8))
    parts = [
        '',
        '        <!-- little rattan waste basket under the desk -->',
        f'        <clipPath id="basketBody"><path d="{body}"/></clipPath>',
        '        <g class="c-sm">',
        f'          <ellipse cx="{cx - 1}" cy="{bot + .5}" rx="{bw + 9}" ry="3.2" fill="#000" opacity=".12"/>',
        f'          <ellipse cx="{cx}" cy="{top}" rx="{tw + 1.8}" ry="5.8" fill="#5C4124"/>',
        f'          <ellipse cx="{cx}" cy="{top + 1}" rx="{tw - 2}" ry="3.6" fill="#3F2C18" opacity=".55"/>',
        f'          <path d="M{cx - tw - 1.8} {top} A{tw + 1.8} 5.8 0 0 1 {cx + tw + 1.8} {top}" stroke="#EFE6D3" stroke-width="2.4" fill="none"/>',
        f'          {inside}',
        f'          <path d="{body}" fill="#A87B45"/>',
        '          <g clip-path="url(#basketBody)">',
        f'            <g fill="none" stroke="#DDB67F" stroke-width="3.3" stroke-linecap="round" stroke-dasharray="4.2 3">{"".join(strands)}</g>',
        f'            <g fill="none" stroke="#FFF1CF" stroke-width=".7" stroke-linecap="round" stroke-dasharray="2.4 4.8" opacity=".55">{"".join(shine)}</g>',
        f'            <rect x="{cx - tw}" y="{bot - 6}" width="{2 * tw}" height="2.6" fill="#8A6236" opacity=".6"/>',
        f'            <path d="{body}" fill="url(#gCylLight)"/>',
        f'            <path d="{body}" fill="url(#gCylShade)"/>',
        '          </g>',
        f'          {basket_cuff(cx, top, tw)}',
        '        </g>',
        '        <!-- one that missed -->',
        f'        <g class="c-sm">{crumple(cx - 40, bot - 3.6, 4.6, 21)}<ellipse cx="{cx - 39}" cy="{bot + .4}" rx="5" ry="1.2" fill="#000" opacity=".12"/></g>',
    ]
    return '\n'.join(parts)


# ------------------------------------------------------------------ desk
KD = 0.08
w('<g transform="translate(0 26)">')
tl = back(560, 588, KD); tr = back(1012, 588, KD)
w(f'''
        <!-- ===== Desk ===== -->
        <g class="c-lg">
          {poly([(880, 602), back(880, 602, KD), back(880, 770, KD), (880, 770)], 'url(#gCabSide)')}
          <path d="M580 600 L590 600 L586 770 L582 770Z" fill="url(#gLeg)"/>
          <path d="M584 592 L590 592 L589 746 L586 746Z" fill="#5A3823"/>
          <rect x="880" y="602" width="120" height="168" rx="2" fill="url(#gCab)"/>
          <rect x="884" y="604" width="112" height="48" rx="2" fill="url(#gShadeV)" opacity=".6"/>''')
for y0 in (606, 660, 714):
    w(f'''          <rect x="886" y="{y0}" width="108" height="50" rx="3" fill="#FCF9F3"/>
          <rect x="886" y="{y0 + 46}" width="108" height="4" rx="2" fill="#000" opacity=".06"/>
          <path d="M927 {y0 + 21} C927 {y0 + 18} 931 {y0 + 16.4} 935 {y0 + 17.4} H945 C949 {y0 + 16.4} 953 {y0 + 18} 953 {y0 + 21} C953 {y0 + 24} 949 {y0 + 25.6} 945 {y0 + 24.6} H935 C931 {y0 + 25.6} 927 {y0 + 24} 927 {y0 + 21}Z" fill="url(#gAntique)"/>
          <path d="M929 {y0 + 20} C930 {y0 + 18.4} 933 {y0 + 17.8} 935 {y0 + 18.4} H945" stroke="#E6CB8E" stroke-width=".7" fill="none" opacity=".8"/>
          <circle cx="932.5" cy="{y0 + 21}" r="1.6" fill="#6E5126"/><circle cx="947.5" cy="{y0 + 21}" r="1.6" fill="#6E5126"/>
          <path d="M932.5 {y0 + 22} C932.5 {y0 + 30.5} 947.5 {y0 + 30.5} 947.5 {y0 + 22}" stroke="#8A6A34" stroke-width="2" fill="none" stroke-linecap="round"/>
          <path d="M934 {y0 + 24.5} C935.5 {y0 + 28} 944.5 {y0 + 28} 946 {y0 + 24.5}" stroke="#E6CB8E" stroke-width=".6" fill="none" opacity=".8"/>''')
w(f'''          {poly([tl, tr, (1012, 588), (560, 588)], 'url(#gDeskTop)')}
          <rect x="558" y="587" width="456" height="15" rx="4" fill="url(#gDeskEdge)"/>
          <rect x="560" y="587" width="452" height="2" fill="#fff" opacity=".6"/>
        </g>''' + waste_basket())

# ------------------------------------------------------------------ mug and phone
HEART = 'M0 3.2 C-3.6 0.4 -4.4 -2.2 -2.4 -3.2 C-1.2 -3.8 0 -2.8 0 -1.8 C0 -2.8 1.2 -3.8 2.4 -3.2 C4.4 -2.2 3.6 0.4 0 3.2Z'


def mug():
    """A speckled pink ceramic mug of latte (with a foam heart) on a cork coaster, steaming."""
    rr = random.Random(5)
    specks = ''.join(f'<circle cx="{rr.uniform(912.5, 942):.1f}" cy="{rr.uniform(556, 583):.1f}" r="{rr.uniform(.25, .5):.2f}"/>' for _ in range(26))
    body = 'M910 552 V583 Q910 587.5 914.5 587.5 H939.5 Q944 587.5 944 583 V552Z'
    return f'''
        <!-- Mug: speckled pink glaze, latte with a foam heart, on a cork coaster -->
        <g class="obj lift" id="o-mug" data-id="mug" tabindex="0" role="button" aria-label="Mug: what fuels me">
          <rect x="904" y="514" width="58" height="80" fill="transparent"/>
          <g class="steam" stroke="#B7BFCD" stroke-width="2" fill="none" stroke-linecap="round" opacity=".75">
            <path d="M921 544 C915 536 927 530 921 520"/><path d="M933 546 C927 536 939 530 933 518" class="s2"/>
          </g>
          <ellipse cx="928" cy="590.6" rx="24" ry="2.6" fill="#000" opacity=".12"/>
          <ellipse cx="927" cy="589.2" rx="22" ry="3.4" fill="#B9874F"/>
          <ellipse cx="927" cy="588" rx="22" ry="3.4" fill="#D8AD76"/>
          <g fill="#A97A45" opacity=".5"><circle cx="910" cy="588.4" r=".5"/><circle cx="916" cy="586.6" r=".4"/><circle cx="941" cy="589.2" r=".5"/><circle cx="946" cy="587.4" r=".4"/><circle cx="935" cy="590" r=".4"/></g>
          <path fill-rule="evenodd" d="M943 556.4 C962.4 556.4 962.4 581.6 943 581.6Z M943 562 C954.8 562 954.8 576 943 576Z" fill="#E79BB1"/>
          <path d="M945 557.8 C957.6 558.6 959.6 570 956 576" stroke="#FBD3DD" stroke-width="1.1" fill="none" stroke-linecap="round" opacity=".8"/>
          <path d="{body}" fill="url(#gMug)"/>
          <g fill="#B5677E" opacity=".35">{specks}</g>
          <path d="M910.3 584.3 H943.7 Q943.4 587.5 939.5 587.5 H914.5 Q910.6 587.5 910.3 584.3Z" fill="#EBDCCB"/>
          <rect x="913.4" y="557" width="1.7" height="23" rx=".85" fill="#FFFFFF" opacity=".45"/>
          <path d="{HEART}" transform="translate(927 569.6) scale(1.35)" fill="#FFFFFF" opacity=".92"/>
          <ellipse cx="927" cy="552" rx="17" ry="3.7" fill="#FDE4EB"/>
          <ellipse cx="927" cy="552.3" rx="15.4" ry="2.9" fill="#E39DB1"/>
          <ellipse cx="927" cy="553" rx="14.2" ry="2.3" fill="#8F6040"/>
          <ellipse cx="927" cy="553" rx="12.4" ry="1.8" fill="#C08B62"/>
          <path d="{HEART}" transform="translate(927 553.1) scale(1.15 .36)" fill="#F7E8D4"/>
        </g>'''


def phone():
    """A phone on an oak stand, open on a little chat: a new message, bubbles, someone typing."""
    w = 'fill="#FFFFFF"'
    return f'''
        <!-- Phone on an oak stand, open on a "say hello" chat -->
        <g class="obj lift" id="o-phone" data-id="phone" tabindex="0" role="link" aria-label="Phone: go to the Contact page">
          <rect x="954" y="518" width="50" height="74" fill="transparent"/>
          <ellipse cx="980" cy="589.6" rx="26" ry="2.2" fill="#000" opacity=".12"/>
          <path d="M957 583.4 H1001 Q1003.4 583.4 1003.4 585.6 V587.2 H954.6 V585.6 Q954.6 583.4 957 583.4Z" fill="url(#gOakF)"/>
          <rect x="954.6" y="587.2" width="48.8" height="1.8" rx=".6" fill="#C6A97F"/>
          <g transform="rotate(-12 980 584)">
            <rect x="965.2" y="539" width="1.2" height="4.4" rx=".5" fill="#1E2129"/><rect x="965.2" y="546" width="1.2" height="6.6" rx=".5" fill="#1E2129"/>
            <rect x="993.6" y="542" width="1.2" height="8.8" rx=".5" fill="#1E2129"/>
            <rect x="966" y="528" width="28" height="56" rx="5.6" fill="#2F3340"/>
            <rect x="966.4" y="528.4" width="27.2" height="55.2" rx="5.3" fill="none" stroke="#5A6072" stroke-width=".6"/>
            <rect x="967.6" y="529.6" width="24.8" height="52.8" rx="4.3" fill="url(#gPhoneScreen)"/>
            <rect x="976.6" y="531.2" width="6.8" height="2.1" rx="1.05" fill="#1E2129"/>
            <path d="M970 532.3 h3.6" stroke="#2A2F3A" stroke-width=".8" stroke-linecap="round"/>
            <rect x="986.6" y="531.6" width="3.2" height="1.4" rx=".4" fill="none" stroke="#2A2F3A" stroke-width=".45"/><rect x="987" y="532" width="2" height=".6" fill="#2A2F3A"/>
            <rect x="969.2" y="535.2" width="21.6" height="6.2" rx="2.2" {w} opacity=".95"/>
            <circle cx="972.4" cy="538.3" r="1.7" fill="#F2AFC1"/><path d="M971.4 538.6 q1 .9 2 0" stroke="#FFFFFF" stroke-width=".4" fill="none"/>
            <path d="M975 537.3 h8" stroke="#2A2F3A" stroke-width=".75" stroke-linecap="round" opacity=".75"/>
            <path d="M975 539.5 h12.4" stroke="#2A2F3A" stroke-width=".55" stroke-linecap="round" opacity=".35"/>
            <circle class="ping" cx="990" cy="535.6" r="1.5" fill="#E2707A"/>
            <rect x="969.6" y="545" width="13.4" height="5.4" rx="2.7" {w}/>
            <path d="M971.6 547.7 h9" stroke="#2A2F3A" stroke-width=".6" stroke-linecap="round" opacity=".45"/>
            <rect x="976.4" y="552.6" width="14" height="5.4" rx="2.7" fill="#3A57C4"/>
            <path d="M978.4 555.3 h10" stroke="#FFFFFF" stroke-width=".6" stroke-linecap="round" opacity=".85"/>
            <rect x="969.6" y="560.2" width="10.4" height="5.4" rx="2.7" {w}/>
            <path d="M971.6 562.9 h6" stroke="#2A2F3A" stroke-width=".6" stroke-linecap="round" opacity=".45"/>
            <rect x="969.6" y="567.6" width="9" height="4.4" rx="2.2" {w}/>
            <g class="typing" fill="#9AA1AE"><circle cx="971.9" cy="569.8" r=".6"/><circle cx="974.1" cy="569.8" r=".6"/><circle cx="976.3" cy="569.8" r=".6"/></g>
            <rect x="969.4" y="575" width="21.2" height="4.2" rx="2.1" {w} opacity=".9"/>
            <path d="M971.4 577.1 h8" stroke="#2A2F3A" stroke-width=".5" stroke-linecap="round" opacity=".3"/>
            <circle cx="988.7" cy="577.1" r="1.6" fill="#3A57C4"/><path d="M988 577.1 h1.4 M988.9 576.4 l.6 .7 -.6 .7" stroke="#FFFFFF" stroke-width=".4" fill="none" stroke-linecap="round"/>
            <rect x="976.4" y="580.6" width="7.2" height=".8" rx=".4" fill="#2A2F3A" opacity=".5"/>
            <path d="M968 530 L980 530 L968 552Z" fill="#FFFFFF" opacity=".12"/>
            <rect x="963.2" y="579.6" width="33.6" height="5.4" rx="1.2" fill="url(#gOakF)"/>
            <rect x="963.2" y="579.6" width="33.6" height="1" rx=".5" fill="#FFF6E4" opacity=".8"/>
          </g>
        </g>'''


# ------------------------------------------------------------------ sketchbook
def pencil(x, y, angle, length=64):
    """A yellow hexagonal pencil lying on the desk: eraser, metal band, body, sharpened wood, graphite."""
    b = length - 10                       # where the body ends and the sharpened wood begins
    return f'''<g transform="translate({x} {y}) rotate({angle})">
            <rect x="1" y="1.4" width="{length - 1}" height="4.4" rx="2" fill="#000" opacity=".12"/>
            <rect x="0" y="-2.2" width="5" height="4.4" rx="1.8" fill="#EFA2B5"/><rect x="0" y=".8" width="5" height="1.4" rx=".7" fill="#D9849A"/>
            <rect x="4.4" y="-2.3" width="4.6" height="4.6" fill="#C9CED6"/>
            <path d="M5.6 -2.3 V2.3 M7.2 -2.3 V2.3" stroke="#9AA1AC" stroke-width=".5"/><rect x="4.4" y="-2.3" width="4.6" height="1.1" fill="#EEF1F5"/>
            <rect x="9" y="-2.2" width="{b - 9}" height="1.45" fill="#F9E199"/>
            <rect x="9" y="-.75" width="{b - 9}" height="1.5" fill="#F2CE62"/>
            <rect x="9" y=".75" width="{b - 9}" height="1.45" fill="#D6AA43"/>
            <path d="M{b} -2.2 L{b + 7} -.55 L{b + 7} .55 L{b} 2.2Z" fill="#EBCB9C"/>
            <path d="M{b} .2 L{b + 7} .1 L{b + 7} .55 L{b} 2.2Z" fill="#D2AE7C"/>
            <path d="M{b} -2.2 Q{b + 1} -1.4 {b} -.75 Q{b + 1} 0 {b} .75 Q{b + 1} 1.4 {b} 2.2" fill="none" stroke="#C99E45" stroke-width=".5"/>
            <path d="M{b + 7} -.55 L{length} 0 L{b + 7} .55Z" fill="#3A3F4A"/>
          </g>'''


def sketchbook():
    """An open spiral sketchbook: blue hardback, curved pages, a lightbulb doodle and a checklist,
    a ribbon bookmark and a pencil."""
    gx = 656                                   # the gutter, where the spiral runs
    back, front = 568.5, 586.5                 # back and front edges of the pages
    left_page = f'M611 {front} L621.5 {back} C634 566.4 647 567.2 {gx - 1} {back + 2.6} L{gx - 1} {front + .6} C643 584.6 626 584.6 611 {front}Z'
    right_page = f'M701 {front} L690.5 {back} C678 566.4 665 567.2 {gx + 1} {back + 2.6} L{gx + 1} {front + .6} C669 584.6 686 584.6 701 {front}Z'
    # page content is drawn flat, then squashed and slanted to lie on each page
    bulb = ('<circle cx="14" cy="13" r="6.4" fill="none"/><path d="M10.6 18.6 Q14 21 17.4 18.6 M11.4 21.6 H16.6 M12.2 24.2 H15.8"/>'
            '<path d="M14 2.6 V0 M5 6 L3 4 M23 6 L25 4 M3.4 13 H1 M24.6 13 H27" stroke-dasharray="none"/>'
            '<path d="M12.4 13.6 Q14 10 15.6 13.6" />'
            '<path d="M29 22 C33 18 36 24 40 19" /><path d="M37.6 18.4 L40 19 L39.4 21.4"/>')
    lines_l = '<path d="M10 32 H34 M10 37 H28" stroke-width=".9" opacity=".45"/>'
    check = ''.join(f'<rect x="3" y="{8 + i * 8}" width="4.4" height="4.4" rx=".8" fill="none"/>'
                    + (f'<path d="M3.8 {10.4 + i * 8} l1.4 1.4 l2.6 -3.4" stroke="#3A57C4" stroke-width="1.3"/>' if i < 2 else '')
                    + f'<path d="M10 {10.2 + i * 8} H{30 - i * 5}" stroke-width=".9" opacity=".55"/>' for i in range(3))
    page_ink = 'fill="none" stroke="#3A57C4" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"'
    coils = ''.join(f'<ellipse cx="{gx}" cy="{back + 3.4 + i * 2.15:.2f}" rx="2.3" ry=".75" fill="none" stroke="#8C919C" stroke-width=".75"/>'
                    f'<circle cx="{gx - 2.6}" cy="{back + 3.6 + i * 2.15:.2f}" r=".45" fill="#B9B2A3"/><circle cx="{gx + 2.6}" cy="{back + 3.6 + i * 2.15:.2f}" r=".45" fill="#B9B2A3"/>'
                    for i in range(7))
    return f'''
        <!-- Sketchbook: an open spiral book with a doodle, a checklist, a bookmark and a pencil -->
        <g class="obj lift" id="o-sketch" data-id="sketch" tabindex="0" role="link" aria-label="Sketchbook: go to the Notes page">
          <path d="M606 590.6 L702 590.6 L707 592.4 L601 592.4Z" fill="#000" opacity=".1"/>
          <path d="M617.5 567 L694.5 567 L706.5 588.4 L605.5 588.4Z" fill="#6C7FB8"/>
          <path d="M605.5 588.4 L706.5 588.4 L706.5 590.6 L605.5 590.6Z" fill="#4E619A"/>
          <path d="M608.6 {front + .4} L{gx - 1} {front + 1.2} L{gx - 1} {front + 2.4} L608.6 {front + 1.8}Z" fill="#EFE7D6"/>
          <path d="M703.4 {front + .4} L{gx + 1} {front + 1.2} L{gx + 1} {front + 2.4} L703.4 {front + 1.8}Z" fill="#E7DECB"/>
          <path d="M609 {front + 1.3} L{gx - 1} {front + 2} M703 {front + 1.3} L{gx + 1} {front + 2}" stroke="#D3C8B2" stroke-width=".35"/>
          <path d="{left_page}" fill="#FFFEFA"/>
          <path d="{right_page}" fill="#FAF5E9"/>
          <path d="{left_page}" fill="url(#gGutterL)"/>
          <path d="{right_page}" fill="url(#gGutterR)"/>
          <g transform="translate(620 569.6) matrix(1 0 -.34 .37 0 0)" {page_ink}>{bulb}{lines_l}</g>
          <g transform="translate(661 569.6) matrix(1 0 .32 .37 0 0)" fill="none" stroke="#2A2F3A" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 2.6 H22" stroke="#3A57C4" stroke-width="1.6"/>{check}
          </g>
          <path d="M688 {back + .8} L697.4 {back + .4} L700.6 {back + 6.2} L691 {back + 6.6}Z" fill="#F7DD86"/>
          <path d="M691 {back + 6.6} L700.6 {back + 6.2} L700.9 {back + 6.8} L691.4 {back + 7.2}Z" fill="#E2C36A"/>
          {coils}
          <path d="M{gx - 4} {front + 1} L{gx - 4} {front + 7.2} L{gx - 2.6} {front + 6} L{gx - 1.2} {front + 7.2} L{gx - 1.2} {front + 1}Z" fill="#D9584A"/>
          {pencil(633, 588.6, -10, 60)}
        </g>'''


# ------------------------------------------------------------------ monitor screen
# the little icons from the Work page postcards (drawn on a 100 x 100 grid)
_ICON_STROKE = 'stroke="#3A57C4" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
WORK_ICONS = {
    'leaf': f'<path d="M20 80 C20 40 50 18 84 16 C84 54 60 82 20 80Z" fill="#fff" {_ICON_STROKE}/><path d="M20 80 L62 38" fill="none" {_ICON_STROKE}/>',
    'phone': f'<rect x="30" y="10" width="40" height="80" rx="9" fill="#fff" {_ICON_STROKE}/><path d="M44 19 H56" fill="none" {_ICON_STROKE}/><rect x="38" y="28" width="24" height="16" rx="3" fill="#DCE5FA"/>',
    'laptop': f'<rect x="18" y="20" width="64" height="44" rx="5" fill="#fff" {_ICON_STROKE}/><path d="M8 74 H92 L84 64 H16Z" fill="#fff" {_ICON_STROKE}/><path d="M28 34 H60 M28 44 H50" fill="none" {_ICON_STROKE}/>',
}


def mini_postcard(x, y, w, h, tilt, art, icon, featured=False):
    """A small version of a Work page postcard: art and icon on the left, stamp and lines on the right."""
    cx, cy = x + w / 2, y + h / 2
    aw = w * .46                      # the art panel
    s = min(aw, h - 4) * .62 / 100     # icon scale
    ix, iy = x + 2 + aw / 2 - 50 * s, y + h / 2 - 50 * s
    rx = x + 2 + aw + 3               # where the writing side starts
    out = [f'<g transform="rotate({tilt} {cx:.1f} {cy:.1f})">',
           f'<rect x="{x + .9}" y="{y + 1.3}" width="{w}" height="{h}" rx="1.4" fill="#2A2F3A" opacity=".12"/>']
    if featured:  # airmail border
        out.append(f'<rect x="{x - 1.6}" y="{y - 1.6}" width="{w + 3.2}" height="{h + 3.2}" rx="2" fill="url(#airmailSm)"/>')
    out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1.4" fill="#FBF8F1"/>',
            f'<rect x="{x + 2}" y="{y + 2}" width="{aw:.1f}" height="{h - 4}" rx=".8" fill="url(#{art})"/>',
            f'<g transform="translate({ix:.2f} {iy:.2f}) scale({s:.3f})">{WORK_ICONS[icon]}</g>',
            # stamp in the corner and a round postmark beside it
            f'<rect x="{x + w - 8.6}" y="{y + 2.2}" width="6.4" height="7.4" rx=".4" fill="#FFFEFA" stroke="#D8CFBF" stroke-width=".35" stroke-dasharray=".7 .5"/>',
            f'<rect x="{x + w - 7.6}" y="{y + 3.2}" width="4.4" height="5.4" fill="url(#{art})"/>',
            f'<circle cx="{x + w - 12}" cy="{y + 6.4}" r="3.1" fill="none" stroke="#6E5FA8" stroke-width=".35" opacity=".55"/>',
            # the title and a couple of lines of writing
            f'<path d="M{rx:.1f} {y + h * .52:.1f} h{(x + w - 3 - rx) * .8:.1f}" stroke="#2A2F3A" stroke-width="{1.3 if featured else 1}" opacity=".7" stroke-linecap="round"/>',
            f'<path d="M{rx:.1f} {y + h * .52 + 3.6:.1f} h{(x + w - 3 - rx) * .95:.1f} M{rx:.1f} {y + h * .52 + 6.4:.1f} h{(x + w - 3 - rx) * .6:.1f}" stroke="#2A2F3A" stroke-width=".55" opacity=".28" stroke-linecap="round"/>',
            '</g>']
    return ''.join(out)


def monitor_screen():
    """The monitor shows a tiny version of the Work page: heading, button and project postcards."""
    lines = [
        '<g class="screen">',
        # menu bar
        '<rect x="706" y="446" width="188" height="5" fill="#FFFFFF" opacity=".55"/>',
        '<circle cx="711" cy="448.5" r="1" fill="#2A2F3A" opacity=".6"/>',
        '<path d="M716 448.5 h8 M727 448.5 h6 M736 448.5 h7 M872 448.5 h4 M879 448.5 h10" stroke="#2A2F3A" stroke-width=".9" opacity=".45"/>',
        # the browser window
        '<rect x="719" y="457.4" width="164" height="78" rx="4" fill="#2A2F3A" opacity=".1"/>',
        '<rect x="718" y="456" width="164" height="78" rx="4" fill="#FFFDF9"/>',
        '<path d="M722 456 H878 Q882 456 882 460 V465 H718 V460 Q718 456 722 456Z" fill="#F3EEE5"/>',
        '<circle cx="724.5" cy="460.6" r="1.5" fill="#E2707A"/><circle cx="729.5" cy="460.6" r="1.5" fill="#F2C66B"/><circle cx="734.5" cy="460.6" r="1.5" fill="#8FBF7A"/>',
        '<rect x="770" y="458.4" width="60" height="4.6" rx="2.3" fill="#FFFDF9"/>',
        '<circle cx="773.6" cy="460.7" r=".9" fill="#8FBF7A"/><path d="M776.5 460.7 h22" stroke="#2A2F3A" stroke-width=".8" opacity=".35" stroke-linecap="round"/>',
        # the page heading on one line, swiped with a yellow highlighter, and a "View all" button
        '<path d="M725 470.6 h5" stroke="#3A57C4" stroke-width=".8"/><path d="M732 470.6 h16" stroke="#3A57C4" stroke-width=".8" opacity=".45" stroke-linecap="round"/>',
        '<path d="M722.4 476.6 C748 475.4 782 475 803.4 475.4 L804.2 487.6 C782 488 750 488.2 723.2 488.8Z" fill="#F7DD86" opacity=".92"/>',
        '<path d="M723 486.6 C750 486 782 485.8 803.6 485.6" stroke="#EFC95E" stroke-width="1.4" fill="none" opacity=".7" stroke-linecap="round"/>',
        '<text x="725.2" y="486.2" class="svg-screen lg">Selected <tspan font-style="italic" fill="#3A57C4">work</tspan></text>',
        '<rect class="cursor-blink" x="800.6" y="475.4" width="1.1" height="12.4" fill="#3A57C4"/>',
        '<rect x="846" y="477.4" width="30" height="7.4" rx="3.7" fill="#2A2F3A"/>',
        '<path d="M850 481.1 h14" stroke="#FFFDF9" stroke-width=".8" opacity=".85" stroke-linecap="round"/><path d="M867.4 481.1 h4.4 M869.8 479.3 l2 1.8 -2 1.8" stroke="#FFFDF9" stroke-width=".7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
        # three postcards in a row underneath, the first one featured
        mini_postcard(785, 495, 40, 27, 3, 'gArtBlue', 'phone'),
        mini_postcard(834, 494, 40, 27, -3, 'gArtSun', 'laptop'),
        mini_postcard(727, 493, 50, 35, -2.5, 'gArtGreen', 'leaf', featured=True),
        # the cursor, about to open the featured project
        '<g transform="translate(757 508) scale(.4)"><path d="M3 2 L3 24 L9 18 L13 27 L17 25 L13 16 L21 16 Z" fill="#FFFFFF" stroke="#2A2F3A" stroke-width="1.8" stroke-linejoin="round"/></g>',
        '<rect x="763.4" y="518.4" width="16" height="6" rx="3" fill="#2A2F3A"/>',
        '<text x="766" y="522.8" class="svg-screen tiny">Open ↗</text>',
        # dock
        '<rect x="772" y="538" width="56" height="7.6" rx="3.8" fill="#FFFFFF" opacity=".6"/>',
        ''.join(f'<rect x="{777 + i * 8:.1f}" y="539.5" width="4.6" height="4.6" rx="1.3" fill="{c}"/>' for i, c in enumerate(['#E2707A', '#8EA9E0', '#9FC48A', '#F2C66B', '#BEB2F0', '#2A2F3A'])),
        '<circle cx="787.3" cy="545.2" r=".5" fill="#2A2F3A" opacity=".5"/>',
        '</g>',
    ]
    return '\n            '.join(lines)


# ------------------------------------------------------------------ desk items
w('''
        <!-- Desk lamp: antique brass with a scalloped, pleated shade -->
        <g class="obj" id="o-lamp" data-id="lamp" tabindex="0" role="button" aria-label="Desk lamp: switch the light">
          <rect x="562" y="444" width="128" height="146" fill="transparent"/>
          <ellipse cx="586" cy="584" rx="22" ry="4.6" fill="#9C7A3A"/>
          <path d="M564 584 Q565 578 572 577 H600 Q607 578 608 584Z" fill="url(#gBrass)"/>
          <path d="M574 577 Q582 568 583 560 H589 Q590 568 598 577Z" fill="url(#gBrass)"/>
          <path d="M578 576 L584 562 M582 577 L585 562 M586 577 L586 562 M590 577 L587 562 M594 576 L588 562" stroke="#9C7A3A" stroke-width=".9" opacity=".8"/>
          <circle cx="586" cy="558" r="3.4" fill="url(#gBrass)"/>
          <rect x="584" y="470" width="4" height="88" rx="2" fill="url(#gBrass)"/>
          <rect x="585" y="470" width="1.2" height="88" fill="#FFF3C4" opacity=".7"/>
          <path d="M588 526 H594" stroke="#C9A04A" stroke-width="2.4" stroke-linecap="round"/>
          <circle cx="595" cy="526" r="2.2" fill="url(#gBrass)"/>
          <path d="M586 478 H576" stroke="#C9A04A" stroke-width="2.6" stroke-linecap="round"/>
          <circle cx="575" cy="478" r="2.8" fill="url(#gBrass)"/>
          <circle cx="586" cy="469" r="3.2" fill="url(#gBrass)"/>
          <path d="M588 476 C598 464 614 450 630 450 C644 450 650 460 650 472" stroke="#C9A04A" stroke-width="3.2" fill="none" stroke-linecap="round"/>
          <path d="M589 474 C599 463 614 451 630 451" stroke="#FFF3C4" stroke-width="1" fill="none" opacity=".7"/>
          <circle cx="650" cy="474" r="3" fill="url(#gBrass)"/>
          <path d="M642 477 H658 L684 502 Q678 510 671 504 Q664 512 657 505 Q650 513 643 505 Q636 512 629 504 Q622 510 616 502Z" fill="url(#gShadeBlue)"/>
          <path d="M642.0 477 L616.4 503 M644.0 477 L624.8 505 M646.0 477 L633.2 503 M648.0 477 L641.6 505 M650.0 477 L650.0 503 M652.0 477 L658.4 505 M654.0 477 L666.8 503 M656.0 477 L675.2 505 M658.0 477 L683.6 503" stroke="#6E7D98" stroke-width=".9" opacity=".55"/>
          <path d="M644 478 L624 500" stroke="#E4EBF5" stroke-width="1.6" opacity=".55" stroke-linecap="round"/>
          <ellipse class="bulb" cx="650" cy="505" rx="24" ry="3.6" fill="#FFF6D8"/>
        </g>

''' + sketchbook() + '''

        <!-- Monitor: slim charcoal bezel, sage chin, angled aluminium stand -->
        <g class="obj" id="o-monitor" data-id="monitor" tabindex="0" role="link" aria-label="Monitor: go to the Work page">
          <rect x="764" y="582" width="72" height="4.6" rx="2.3" fill="url(#gAlu)"/>
          <ellipse cx="800" cy="582.2" rx="35" ry="1.6" fill="#F4F3EF"/>
          <path d="M789 560 H811 L818 583 H782Z" fill="url(#gAlu)"/>
          <path d="M790.5 560 L785 582" stroke="#FFFFFF" stroke-width="1" opacity=".7"/>
          <path d="M709 442 H891 Q897 442 897 448 V547 H703 V448 Q703 442 709 442Z" fill="#26282E"/>
          <path d="M703 547 H897 V557 Q897 562 892 562 H708 Q703 562 703 557Z" fill="url(#gChin)"/>
          <rect x="703" y="547" width="194" height="1" fill="#000" opacity=".12"/>
          <circle cx="800" cy="444.4" r=".8" fill="#5C6070"/>
          <rect x="706" y="446" width="188" height="102" rx="2" fill="url(#gWallpaper)"/>
''' + '          ' + monitor_screen() + '''
          <path d="M706 446 L760 446 L706 500Z" fill="#FFFFFF" opacity=".08"/>
        </g>
        <!-- Keyboard + mouse -->
        <g class="c-sm">
          <path d="M732 576 H868 L878 587 H722Z" fill="#F8F6F1"/>
          <rect x="722" y="587" width="156" height="2.5" rx="1" fill="#CFCAC0"/>''')
keys = []
for r, (y, x0, x1) in enumerate([(578, 736, 864), (581.5, 732, 868), (584.5, 728, 872)]):
    n = 16
    step = (x1 - x0) / n
    for i in range(n):
        keys.append(f'<rect x="{x0 + i * step + .6:.1f}" y="{y}" width="{step - 1.8:.1f}" height="2.2" rx=".6"/>')
w('          <g fill="#DDD8CE">' + ''.join(keys) + '</g>')
w('''          <ellipse cx="891" cy="584" rx="8" ry="3.6" fill="#F8F6F1"/>
          <path d="M891 581 V584" stroke="#D3CEC4" stroke-width="1"/>
        </g>

''' + mug() + phone())

w('</g>')
# ------------------------------------------------------------------ chair (in front of the desk)
w('<g transform="translate(0 40)">')
w('''
        <!-- Chair: rounded charcoal upholstered shell on tapered walnut legs -->
        <g class="c-sm" transform="translate(796 796) scale(1.4) translate(-796 -794)">
          <ellipse cx="796" cy="792" rx="66" ry="7" fill="#4E3320" opacity=".24"/>
          <path d="M766 712 L759 770 L763 770 L771 712Z M826 712 L833 770 L837 770 L830 712Z" fill="#6C3B1E"/>
          <path d="M746 716 L734 794 L741 794 L754 716Z" fill="url(#gLegW)"/>
          <path d="M846 716 L858 794 L851 794 L838 716Z" fill="url(#gLegW)"/>
          <path d="M734 706 Q794 694 856 704 Q862 714 854 722 Q794 734 738 722 Q730 714 734 706Z" fill="url(#gUpholSeat)"/>
          <path d="M748 720 C740 690 738 652 748 628 C760 606 830 604 842 628 C852 652 850 690 842 720 Q795 732 748 720Z" fill="url(#gUphol)"/>
          <path d="M751 630 C764 612 828 610 840 630 C828 621 764 621 751 630Z" fill="#8A909B"/>
        </g>''')

w('</g>')
# ------------------------------------------------------------------ monstera
w('<g transform="translate(0 22)">')
PX, PY = 1122, 680   # where the stems leave the pot
# Like a real monstera: long stalks fan up out of the pot, and each leaf hangs from the top of
# its stalk by the notch, tip pointing down and out. Big split leaves at the back, two leaves
# seen edge-on at the sides (a very narrow scale x), small young leaves in front.
# The lighter half of every leaf faces the window on the left.
MON = {'A': ('#3E7B44', '#23502A'), 'B': ('#4A8A4D', '#2C5F32'), 'C': ('#356D3C', '#1D4524')}
leaves = [  # stalk top x, y, rotation (0 = tip up, 180 = hanging straight down), scale x, scale y, kind, colour
    (1094, 482, -146, .5, .5, 'mature', 'A'),
    (1158, 470, 152, .5, .52, 'split', 'B'),
    (1074, 548, -120, .16, .42, 'young', 'C'),
    (1192, 556, 122, .17, .44, 'young', 'A'),
    (1080, 566, -158, .4, .4, 'mature', 'B'),
    (1140, 540, 168, .42, .44, 'split', 'A'),
    (1170, 600, 146, .3, .32, 'young', 'B'),
    (1104, 612, -164, .24, .26, 'young', 'C'),
]
w('''
        <!-- Monstera: tall, dark leaves in a concrete planter -->
        <g class="obj plant" id="o-plant" data-id="plant" tabindex="0" role="button" aria-label="Monstera: water the plant">
          <g class="leaves">''')
for i, (x, y, r, sx, sy, kind, col) in enumerate(leaves):
    light, dark = MON[col]
    bx = PX + (x - PX) * .08                      # stalks leave the soil a little apart
    c1x, c1y = bx + (x - PX) * .1, PY - (PY - y) * .5
    c2x, c2y = x - (x - PX) * .12, y + (PY - y) * .28
    sw = 1.8 + 3.2 * max(sx, sy)                  # bigger leaves, thicker stalks
    # turn the leaf over when it hangs, so its lighter half stays on the window side
    mx = -sx if math.cos(math.radians(r)) < 0 else sx
    w(f'''            <g class="lf" style="--t:{4.6 + i * .45:.2f}s; --dl:-{(i * 1.3) % 4:.1f}s">
              <path d="M{bx:.0f} {PY} C{c1x:.0f} {c1y:.0f} {c2x:.0f} {c2y:.0f} {x} {y}" stroke="#2F5A30" stroke-width="{sw:.1f}" fill="none" stroke-linecap="round"/>
              <path d="M{bx - 1:.0f} {PY - 2} C{c1x - 1:.0f} {c1y:.0f} {c2x - 1:.0f} {c2y:.0f} {x - 1} {y}" stroke="#6E9C5E" stroke-width="{sw * .3:.1f}" fill="none" stroke-linecap="round" opacity=".8"/>
              <g transform="translate({x} {y}) rotate({r}) scale({mx} {sy})">
                <use href="#mleaf-{kind}" fill="{light}"/>
                <use href="#mshade-{kind}" fill="{dark}"/>
                <use href="#mveins-{kind}" opacity="{.7 if kind != 'young' else .55}"/>
              </g>
            </g>''')
specks = ''.join(f'<circle cx="{rnd.uniform(1070, 1156):.1f}" cy="{rnd.uniform(694, 772):.1f}" r="{rnd.uniform(.5, 1.2):.1f}"/>' for _ in range(22))
w(f'''          </g>
          <path d="M1074 684 H1170 V774 Q1170 780 1162 780 H1082 Q1074 780 1074 774Z" fill="url(#gConcrete)"/>
          <rect x="1074" y="774" width="96" height="6" rx="3" fill="#000" opacity=".1"/>
          <ellipse cx="1122" cy="684" rx="48" ry="5.5" fill="#9DA09E"/>
          <ellipse cx="1122" cy="684.6" rx="43" ry="4" fill="url(#gSoil)"/>
        </g>''')

w('</g>')

# ------------------------------------------------------------------ light overlays
w('''
        <!-- ===== Light ===== -->
        <rect class="tint" x="-3000" y="-3000" width="7200" height="7000" mask="url(#unlit)"/>
        <!-- warm colour of lamplight inside each pool (multiplies over the uncovered room) -->
        <g class="warmlight" pointer-events="none">
          <ellipse cx="660" cy="590" rx="230" ry="160" fill="url(#gWarmPool)"/>
          <ellipse cx="68" cy="430" rx="170" ry="250" fill="url(#gWarmPool)"/>
          <ellipse cx="438" cy="300" rx="120" ry="100" fill="url(#gWarmPool)"/>
        </g>
        <!-- lit shades: the floor lamp and desk lamp glow from inside when on -->
        <g class="shadelit" pointer-events="none">
          <g transform="translate(-22 58)">
            <path d="M54 297 H126 Q132 297 132 303 V324 Q132 330 126 330 H54 Q48 330 48 324 V303 Q48 297 54 297Z" fill="url(#gShadeLitGlass)" opacity=".42"/>
            <ellipse cx="90" cy="303.5" rx="15" ry="2.8" fill="#FFF8E2"/>
            <ellipse cx="90" cy="315" rx="10" ry="2" fill="#FFE9BC" opacity=".85"/>
            <ellipse cx="90" cy="329.4" rx="34" ry="2.4" fill="#FFEFC8" opacity=".55"/>
          </g>
          <g transform="translate(0 26)">
            <path d="M642 477 H658 L684 502 Q678 510 671 504 Q664 512 657 505 Q650 513 643 505 Q636 512 629 504 Q622 510 616 502Z" fill="url(#gShadeLitFabric)" opacity=".3"/>
            <ellipse cx="650" cy="505" rx="22" ry="3.2" fill="#FFF6DA" opacity=".9"/>
          </g>
        </g>
        <!-- the monitor keeps its true colours (the screen glows on its own): daylight and lamp glow skip it (the desk group sits 26 lower) -->
        <mask id="noChin" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="7200" height="7000"><rect x="-3000" y="-3000" width="7200" height="7000" fill="#fff"/><path transform="translate(0 26)" d="M709 442 H891 Q897 442 897 448 V557 Q897 562 892 562 H708 Q703 562 703 557 V448 Q703 442 709 442Z" fill="#000"/></mask>
        <g class="daylight" pointer-events="none" mask="url(#noChin)">
          <path d="M640 438 L928 438 L1060 772 L700 772Z" fill="url(#gBeam)" filter="url(#soft)"/>
          <path d="M880 792 L990 792 L1012 822 L894 822Z M1002 792 L1112 792 L1136 822 L1024 822Z M898 830 L1016 830 L1040 866 L914 866Z M1028 830 L1146 830 L1174 866 L1052 866Z" style="fill:var(--sun)" opacity=".5" filter="url(#edge1)"/>
        </g>
        <g class="lamplight" pointer-events="none" mask="url(#noChin)">
          <ellipse cx="652" cy="560" rx="200" ry="150" fill="url(#gLampAmbient)" opacity=".55"/>
          <path d="M624 534 L676 534 L748 618 L556 618Z" fill="url(#gCone)" filter="url(#lampBlur)"/>
          <ellipse cx="652" cy="614" rx="104" ry="16" fill="url(#gLampPool)" filter="url(#lampBlur)"/>
          <ellipse cx="650" cy="536" rx="34" ry="12" fill="url(#gLampPool)" filter="url(#lampBlur)"/>
        </g>
        <g class="lamplight" pointer-events="none" mask="url(#noChin)">
          <ellipse cx="68" cy="374" rx="110" ry="90" fill="url(#gLampAmbient)" opacity=".6"/>
          <ellipse cx="68" cy="490" rx="80" ry="130" fill="url(#gLamp)" opacity=".55"/>
          <ellipse cx="68" cy="362" rx="22" ry="6" fill="url(#gLampPool)" filter="url(#lampBlur)"/>
          <ellipse cx="68" cy="389" rx="44" ry="8" fill="url(#gLampPool)" filter="url(#lampBlur)" opacity=".8"/>
        </g>
        <g class="lamplight" pointer-events="none" mask="url(#noChin)"><ellipse cx="438" cy="284" rx="92" ry="64" fill="url(#gLamp)"/><path d="M290 297 C290 285 302 277 316 277 C330 277 342 285 342 297 C342 301 336 302 316 302 C296 302 290 301 290 297Z" transform="translate(438 329) scale(1.25) translate(-316 -329)" fill="#FFE9B0" opacity=".55"/></g>
        <ellipse class="awardlight" cx="350" cy="526" rx="46" ry="26" fill="currentColor" filter="url(#soft)" pointer-events="none"/>
        <g transform="translate(0 30)" pointer-events="none">
          <use class="figglow" href="#figs" filter="url(#figGlow)"/>
          <use class="figlit" href="#figs"/>
        </g>
        <rect class="glare" x="706" y="472" width="188" height="102" rx="3" pointer-events="none"/>''')


def cyl(id, base, hi, sh, h0=.12, h1=.26, s0=.66):
    return lg(id, S((0, base), (h0, base), (h0, hi), (h1, hi), (h1, base), (s0, base), (s0, sh), (1, sh)), **H)
def bandv(id, top, base, bot, a=.14, b=.8):
    return lg(id, S((0, top), (a, top), (a, base), (b, base), (b, bot), (1, bot)), **V)
def split(id, light, dark, at=.52):
    return lg(id, S((0, light), (at, light), (at, dark), (1, dark)), **H)
CEL = {}
for d_ in [
    cyl('gTerra', '#E08A5C', '#F6B48A', '#BF663E'), cyl('gCeramic', '#F5F0E8', '#FFFFFF', '#D6CCBC'),
    cyl('gClay', '#EBCFC0', '#F7E5DA', '#D4AE9A'),
    cyl('gLilac', '#CFC6F2', '#EAE5FC', '#A598DD'), cyl('gMug', '#F2AFC1', '#FDD9E3', '#D4879E'),
    cyl('gGold', '#E9C35E', '#FCEBAE', '#B6882E'), cyl('gAlu', '#E7E5E0', '#FFFFFF', '#BCB8B0'),
    cyl('gMetal', '#5F6470', '#8D93A0', '#41454E'), cyl('gShade', '#EEC765', '#FCE8A8', '#CC9B3A'),
    '<radialGradient id="gGuitar" cx=".36" cy=".34" r=".78"><stop offset="0" stop-color="#F7CC96"/><stop offset=".55" stop-color="#E4A365"/><stop offset="1" stop-color="#C27D43"/></radialGradient>',
    cyl('gClockRim', '#F3E6CF', '#FFFFFF', '#D6C3A3'),
    bandv('gBrass', '#F8E2A2', '#E2BA5B', '#B58A38', .3, .7),
    bandv('gChairBack', '#CDE2BF', '#A9C49B', '#84A476', .16, .8), bandv('gChairSeat', '#C2D8B4', '#A3BF95', '#7E9E71', .35, .7),
    bandv('gRecord', '#FFFBF3', '#F1EADF', '#D9CFBE'), bandv('gBasket', '#ECCB98', '#D6AE77', '#B68A53', .1, .78),
    bandv('gDeskEdge', '#B88560', '#8E5D3D', '#6C4329', .22, .74), bandv('gOakEdge', '#B4805A', '#93613F', '#704629', .25, .78),
    split('gPothos', '#62B249', '#3C8A34', .5), split('gPothosB', '#7BC458', '#479A3D', .5), split('gPothosC', '#56A443', '#2F7A2F', .5),
    bandv('gFabric', '#93A86E', '#74894F', '#56683A', .2, .78), cyl('gWalnut', '#9B5A31', '#C9844F', '#6C3B1E', .12, .26, .7),
    cyl('gShadeBlue', '#8E9DB8', '#BAC6DA', '#6E7D98', .16, .34, .7),
    lg('gUphol', S((0, '#656B75'), (.32, '#7B818B'), (.72, '#555A63'), (1, '#41454D')), **H), lg('gUpholSeat', S((0, '#6E747E'), (1, '#454A52')), **V),
    lg('gLegW', S((0, '#B97543'), (1, '#7A4423')), **H),
    split('gOxa', '#5E2454', '#3D1437', .5), cyl('gStone', '#55595F', '#71767D', '#3A3D42', .14, .3, .7),
    lg('gOpal', S((0, '#EFE4CA'), (.3, '#FFFCF3'), (.7, '#EADDC0'), (1, '#D6C6A4')), **H), lg('gBronze', S((0, '#544433'), (.35, '#8A7352'), (.7, '#5A4A37'), (1, '#3A2F23')), **H),
    cyl('gRattan', '#D9B27A', '#EFD3A0', '#B78A53', .1, .24, .64), cyl('gLiner', '#F6EFDF', '#FFFDF6', '#E3D7BF', .1, .24, .64),
    split('gMonA', '#3E7B44', '#23502A', .53), split('gMonB', '#4A8A4D', '#2C5F32', .53), split('gMonC', '#356D3C', '#1D4524', .53),
    lg('gConcrete', S((0, '#9A9D9B'), (.3, '#B4B7B5'), (.75, '#8B8E8C'), (1, '#6F7270')), **H),
    lg('gPleat', S((0, '#000', .12), (.12, '#000', .12), (.12, '#fff', .16), (.26, '#fff', .16), (.26, '#000', 0), (.4, '#000', 0), (.4, '#000', .14), (.52, '#000', .14), (.52, '#fff', .12), (.66, '#fff', .12), (.66, '#000', 0), (.8, '#000', 0), (.8, '#000', .16), (1, '#000', .16)), **H),
    bandv('gDarkWood', '#8A6442', '#5A3E28', '#3B2818', .28, .7),
    lg('gHatbox', S((0, '#F3ECE2'), (.35, '#FBF7F1'), (1, '#DCD1C1')), **H),
    lg('gCert', S((0, '#F6F3EE'), (1, '#E9E4DD')), **D),
    lg('gCalCard', S((0, '#FFFDF8'), (1, '#F2ECE0')), **V), lg('gCalSky', S((0, '#7FAEE0'), (1, '#BCD6F0')), **V),
    '<radialGradient id="gFig" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#EEF9D6"/><stop offset=".7" stop-color="#CFE6A8"/><stop offset="1" stop-color="#B5D58C"/></radialGradient>',
    lg('gCaseWood', S((0, '#D69A60'), (.5, '#C9874E'), (1, '#B0703C')), **V),
    lg('gWalnutCase', S((0, '#8E5C3B'), (.5, '#7E4F31'), (1, '#6A4128')), **V),
    lg('gPlatterSide', S((0, '#2C2E34'), (.45, '#3A3D45'), (1, '#121317')), **H),
    lg('gRugTop', S((0, '#EFE7DA'), (.5, '#F4EEE3'), (1, '#E9DFCF')), **V),
    lg('gPersian', S((0, '#E3DACB'), (.5, '#EAE2D5'), (1, '#E4DBCC')), **V),
    lg('gAntique', S((0, '#C9A764'), (.5, '#A88645'), (1, '#7E6030')), **V),
    lg('gChin', S((0, '#4864CE'), (1, '#3550BA')), **V), lg('gWallpaper', S((0, '#F6D9CF'), (.5, '#E5D9F0'), (1, '#CFE0F3')), **D),
    lg('gHatboxBlue', S((0, '#C9D8EA'), (.35, '#E2EBF6'), (1, '#A9BDD8')), **H),
    lg('gShadeLitGlass', S((0, '#E9DCC4'), (.5, '#F7EBD2'), (1, '#E2CFAE')), **V), lg('gShadeLitFabric', S((0, '#C7CFDC'), (.55, '#E5DDD0'), (1, '#FFEFCF')), **V),
    lg('gSea', S((0, '#C8DCEB'), (1, '#AFCBE2')), **V),
    lg('gPortraitBg', S((0, '#FBE9E4'), (1, '#E9EEF8')), **V),
    lg('gRedDome', S((0, '#C93A2E'), (.3, '#EE5A4C'), (.7, '#CF3A2E'), (1, '#A3271F')), **H), lg('gRedBase', S((0, '#B32E24'), (.35, '#E24E40'), (.7, '#BE3328'), (1, '#8E211B')), **H),
    cyl('gChrome', '#BFC4CB', '#FFFFFF', '#868C95', .2, .4, .72),
    split('gLeaf', '#6DB34F', '#3F8A3A'), split('gLeafB', '#88C962', '#4E9A43'), split('gLeafC', '#5AA145', '#2E7133'),
    split('gNeck', '#9A6440', '#6E432A', .5), split('gLeg', '#8E5D3D', '#62402A', .5),
    lg('gShadeH', S((0, '#fff', .22), (.14, '#fff', .22), (.14, '#fff', 0), (.74, '#000', 0), (.74, '#000', .18), (1, '#000', .18)), **H),
    lg('gShadeV', S((0, '#fff', .26), (.22, '#fff', .26), (.22, '#fff', 0), (.76, '#000', 0), (.76, '#000', .16), (1, '#000', .16)), **V),
    lg('gCelShade', S((0, '#3B2410', .26), (.62, '#3B2410', .26), (.62, '#3B2410', 0), (1, '#3B2410', 0)), **V),
    lg('gCurtain', S((0, '#F8E6EC'), (.13, '#F8E6EC'), (.13, '#E8C3D0'), (.23, '#E8C3D0'), (.23, '#F8E6EC'), (.42, '#F8E6EC'), (.42, '#E8C3D0'), (.52, '#E8C3D0'), (.52, '#F8E6EC'), (.7, '#F8E6EC'), (.7, '#E4BECB'), (.84, '#E4BECB'), (.84, '#F3DDE4'), (1, '#F3DDE4')), **H),
    lg('gOakF', S((0, '#8E5E3E'), (1, '#7A4C30')), **D), lg('gOakSide', S((0, '#6A4128'), (1, '#5C3822')), **H),
    lg('gOakTop', S((0, '#7E5235'), (1, '#986646')), **V), lg('gCBack', S((0, '#5C3A24'), (1, '#6C462D')), **V),
    lg('gInL', S((0, '#4C2F1D'), (1, '#553522')), **H), lg('gInR', S((0, '#8E6040'), (1, '#83573A')), **H),
    lg('gInTop', S((0, '#462B1A'), (1, '#50321F')), **V),
    lg('gDeskTop', S((0, '#7A4E32'), (1, '#9A6848')), **V),
    lg('gFloor', S((0, '#CDB89B'), (.3, '#D9C7AC'), (1, '#CAB394')), **V),
    '<linearGradient id="gWall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--wall-1)"/><stop offset=".55" style="stop-color:var(--wall-2)"/><stop offset="1" style="stop-color:var(--wall-3)"/></linearGradient>',
    '<linearGradient id="gWains" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--wains-1)"/><stop offset="1" style="stop-color:var(--wains-2)"/></linearGradient>', lg('gBase', S((0, '#FFF8EC'), (1, '#E4DACB')), **V),
    lg('gCabSide', S((0, '#D3C6B0'), (1, '#C9BBA4')), **H),
]:
    CEL[re.search(r'id="(\w+)"', d_).group(1)] = d_
known = set()
for i_, d_ in enumerate(defs):
    m_ = re.match(r'<linearGradient id="(\w+)"', d_)
    if m_ and m_.group(1) in CEL:
        defs[i_] = CEL[m_.group(1)]; known.add(m_.group(1))
for k_, d_ in CEL.items():
    if k_ not in known: defs.append(d_)

defs = [d_.replace('@@MONSTERA@@', _monstera_defs()) for d_ in defs]
inner = '\n        <defs>\n          ' + '\n          '.join(defs) + '\n        </defs>\n\n        ' + '\n        '.join(out) + '\n      '

p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'pages', 'index.html')
s = open(p).read()
a = s.index('<svg class="room"')
a = s.index('>', a) + 1
b = s.index('</svg>', a)
s = s[:a] + inner + s[b:]
open(p, 'w').write(s)
print('ok', len(inner))
