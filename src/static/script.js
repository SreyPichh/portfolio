/* =========================================================
   Portfolio interactions
   - the home office: clickable objects
   - wall clock: time of day (dawn → day → golden hour → night)
   - desk lamp, window view that shifts with the cursor
   - quote reveal (about page)
   - project postcards → story dialog, draggable desk notes
   - copy-to-clipboard email, soft cursor ring
   ========================================================= */
(function () {
  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = window.matchMedia('(pointer: fine)').matches;
  const NS = 'http://www.w3.org/2000/svg';
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const hero = document.getElementById('prologue');

  /* ---------- Placeholder projects: edit these ----------
     Add a real picture with  cover: 'assets/project-one.jpg'  (put the file in src/static/assets/).
     Without one, the card shows the drawn icon on the art colour. */
  const projects = [
    { title: 'Project One', tag: 'Brand identity', dur: '3m', year: '2026', icon: 'leaf',
      summary: '[One sentence: what it is, who it was for, and why it mattered.]',
      art: 'linear-gradient(160deg,#E3F0D6,#B9D3A8)' },
    { title: 'Project Two', tag: 'Mobile app', dur: '2m', year: '2025', icon: 'phone',
      summary: '[One sentence: the problem in plain words.]',
      art: 'linear-gradient(160deg,#E4ECFA,#B9CCF1)' },
    { title: 'Project Three', tag: 'Website design', dur: '6w', year: '2025', icon: 'laptop',
      summary: '[One sentence: what changed because of this work.]',
      art: 'linear-gradient(160deg,#FCF3D6,#F3DC94)' },
    { title: 'Project Four', tag: 'Packaging', dur: '1m', year: '2024', icon: 'box',
      summary: '[One sentence: the most surprising thing about this project.]',
      art: 'linear-gradient(160deg,#FBE6EC,#F2BFCF)' },
    { title: 'Project Five', tag: 'Side project', dur: '∞', year: 'Ongoing', icon: 'star',
      summary: '[One sentence: the thing you make just because you love it.]',
      art: 'linear-gradient(160deg,#ECE8FB,#CFC6F2)' },
  ];

  const beats = [
    ['The problem', '[What was broken, missing or confusing? Who felt it? Set the scene in two or three sentences.]'],
    ['The first try', '[What did you do first? Show a sketch or an early version. It is fine if it was a little wrong.]'],
    ['What went wrong', '[The stumble: user feedback, a constraint, a moment of doubt. This is where readers lean in.]'],
    ['What shipped', '[The final work. Add two or three images and one number if you have it (sign-ups, time saved, smiles).]'],
    ['What I learned', '[One honest lesson you carried into the next project.]'],
  ];

  const S = 'stroke="#3A57C4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"';
  const icons = {
    leaf: `<path d="M20 80 C20 40 50 18 84 16 C84 54 60 82 20 80Z" fill="#fff" ${S}/><path d="M20 80 L62 38" fill="none" ${S}/>`,
    phone: `<rect x="30" y="10" width="40" height="80" rx="9" fill="#fff" ${S}/><path d="M44 19 H56" fill="none" ${S}/><rect x="38" y="28" width="24" height="16" rx="3" fill="#DCE5FA"/>`,
    laptop: `<rect x="18" y="20" width="64" height="44" rx="5" fill="#fff" ${S}/><path d="M8 74 H92 L84 64 H16Z" fill="#fff" ${S}/><path d="M28 34 H60 M28 44 H50" fill="none" ${S}/>`,
    box: `<path d="M50 12 L86 30 V70 L50 88 L14 70 V30Z" fill="#fff" ${S}/><path d="M14 30 L50 48 L86 30 M50 48 V88" fill="none" ${S}/>`,
    star: `<path d="M50 10 L61 38 L90 40 L67 58 L75 88 L50 71 L25 88 L33 58 L10 40 L39 38Z" fill="#fff" ${S}/>`,
  };

  /* =========================================================
     Time of day — set by the wall clock
     ========================================================= */
  const KEYS = ['sky-1','sky-2','sky-3','mount-1','mount-2','hb-1','hb-2','hm-1','hm-2','hf-1','hf-2','tree','tree-2','cloud','cloud-shade','sun','sun-edge','glow'];
  const PALETTES = {
    dawn:   ['#A9B9E2','#E8CCDB','#FBE6D2','#CBC6E0','#EBDCE4','#CEDFB9','#B6CFA0','#AAC991','#90B778','#8EB874','#74A05E','#5F8A59','#4B7548','#FFF5F1','#EBD3DE','#FFE2C6','#FFB99A','#FFE6D2'],
    day:    ['#8FBCE8','#C4DEF3','#F1EEE4','#C3D5EA','#DFE8EE','#CFE3B6','#B2D198','#A6CC88','#8ABA6E','#8BBD6B','#6CA155','#5A8C55','#46733F','#FFFFFF','#DCE7F2','#FFF1C4','#FFD98C','#FFF6DA'],
    golden: ['#E7B4A6','#F6D2A9','#FBEBCB','#D9BBB6','#EED7C6','#D8D79C','#C0C680','#B6BF74','#9CAA5F','#95A95B','#7A9049','#64794A','#4F6239','#FFF1E0','#EFCAB6','#FFD79A','#FFA766','#FFDDB0'],
    night:  ['#121939','#283062','#544F80','#333B68','#434A79','#34505A','#2B444D','#2A4446','#223A3C','#213834','#1A2E2B','#192B2A','#132220','#3C4576','#2B3361','#F6F1DC','#C9C6E8','#AEB6EE'],
  };
  // how the room itself is tinted (multiplied over everything but the window and screen)
  const TINTS = { dawn: '#F7E0E6', day: '#FFFFFF', golden: '#FFDDB8', night: '#4A5390' };
  const STOPS = [[0, 'dawn'], [0.35, 'day'], [0.7, 'golden'], [1, 'night']];
  const PRESETS = [0, 0.35, 0.7, 1];

  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const mix = (a, b, k) => {
    const A = hex(a), B = hex(b);
    return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * k).toString(16).padStart(2, '0')).join('');
  };

  const room = document.getElementById('room');
  const winSun = document.getElementById('win-sun');
  const handH = document.getElementById('hand-h');
  const handM = document.getElementById('hand-m');
  const clockObj = document.getElementById('o-clock');
  const clock = document.getElementById('clock');
  const phase = document.getElementById('phase');
  let daytime = typeof window.__daytime === 'number' ? window.__daytime : 0.35;
  let dark = 0;
  let lampOn = true;
  try { lampOn = localStorage.getItem('lamp') !== 'off'; } catch (e) {}

  function phaseName(t) {
    if (t < 0.15) return 'dawn';
    if (t < 0.3) return 'morning';
    if (t < 0.48) return 'midday';
    if (t < 0.62) return 'afternoon';
    if (t < 0.78) return 'golden hour';
    if (t < 0.88) return 'dusk';
    return 'night';
  }

  function setLamp() {
    root.style.setProperty('--lamp', lampOn ? (0.18 + 0.82 * dark).toFixed(3) : 0);
    // at night each lamp opens a soft pool of light in the dark room
    root.style.setProperty('--lamp-vis', lampOn ? dark.toFixed(3) : 0);
    room?.classList.toggle('lamp-off', !lampOn);
  }

  function applyTime(t) {
    daytime = clamp(t);
    let i = 0;
    while (i < STOPS.length - 2 && daytime > STOPS[i + 1][0]) i++;
    const [t0, n0] = STOPS[i], [t1, n1] = STOPS[i + 1];
    const k = clamp((daytime - t0) / (t1 - t0));
    KEYS.forEach((key, j) => root.style.setProperty('--' + key, mix(PALETTES[n0][j], PALETTES[n1][j], k)));
    root.style.setProperty('--tint', mix(TINTS[n0], TINTS[n1], k));

    dark = clamp((daytime - 0.72) / 0.2);
    root.style.setProperty('--dark', dark.toFixed(3));
    root.style.setProperty('--beam', (daytime < 0.88 ? Math.sin(Math.PI * daytime / 0.88) : 0).toFixed(3));
    root.style.setProperty('--stars', clamp((daytime - 0.78) / 0.15).toFixed(3));
    root.style.setProperty('--moon', clamp((daytime - 0.82) / 0.08).toFixed(3));
    const theme = daytime > 0.86 ? 'night' : 'day';
    if (root.getAttribute('data-theme') !== theme) root.setAttribute('data-theme', theme);
    setLamp();

    // the sun (and later the moon) crosses the window
    const sx = 650 + daytime * 260;
    const sy = 360 - 200 * Math.sin(Math.PI * (0.2 + 0.6 * daytime));
    winSun?.setAttribute('transform', `translate(${sx.toFixed(1)} ${sy.toFixed(1)})`);

    // the wall clock + the little readout
    const mins = Math.round((5 + daytime * 18) * 60);
    const h = Math.floor(mins / 60) % 24, m = mins % 60;
    handH?.setAttribute('transform', `rotate(${((h % 12) * 30 + m * 0.5).toFixed(1)} 1084 176)`);
    handM?.setAttribute('transform', `rotate(${(m * 6).toFixed(1)} 1084 176)`);
    const time = String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0');
    if (clock) clock.textContent = time;
    if (phase) phase.textContent = phaseName(daytime);
    clockObj?.setAttribute('aria-label', `Wall clock: it's ${time}, ${phaseName(daytime)}. Change the time of day`);
  }
  function saveTime() { try { localStorage.setItem('daytime', daytime.toFixed(3)); } catch (e) {} }

  let tween = null;
  function tweenTo(target) {
    cancelAnimationFrame(tween);
    const from = daytime, start = performance.now(), dur = reduceMotion ? 1 : 1600;
    const step = (now) => {
      const k = clamp((now - start) / dur);
      const e = 1 - Math.pow(1 - k, 3);
      applyTime(from + (target - from) * e);
      if (k < 1) tween = requestAnimationFrame(step); else saveTime();
    };
    tween = requestAnimationFrame(step);
  }
  const nextPreset = () => { const n = PRESETS.find((p) => p > daytime + 0.02); return n === undefined ? 0 : n; };

  applyTime(daytime);

  clockObj?.addEventListener('keydown', (e) => {
    const map = { ArrowRight: 0.04, ArrowUp: 0.04, ArrowLeft: -0.04, ArrowDown: -0.04 };
    if (e.key in map) { e.preventDefault(); cancelAnimationFrame(tween); applyTime(daytime + map[e.key]); saveTime(); }
  });

  /* ---------- Seeded random so the meadow looks the same each visit ---------- */
  let seed = 7;
  const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const petals = ['var(--daisy)', 'var(--daisy)', 'var(--butter)', 'var(--petal)', 'var(--lilac)'];

  function bloom(g, count, x0, x1, y0, y1) {
    for (let i = 0; i < count; i++) {
      const x = x0 + rand() * (x1 - x0);
      const y = y0 + rand() * (y1 - y0);
      const r = 1.6 + rand() * 3 * ((y - y0) / (y1 - y0) + 0.4);
      const c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', x.toFixed(1));
      c.setAttribute('cy', y.toFixed(1));
      c.setAttribute('r', r.toFixed(1));
      c.setAttribute('fill', petals[Math.floor(rand() * petals.length)]);
      c.setAttribute('opacity', (0.75 + rand() * 0.25).toFixed(2));
      g.appendChild(c);
    }
  }
  const wide = document.querySelectorAll('.flowers.wide');
  if (wide[0]) bloom(wide[0], 140, 0, 1440, 505, 598);
  if (wide[1]) bloom(wide[1], 70, 0, 1440, 470, 498);

  /* ---------- Toast ---------- */
  const toast = document.querySelector('.toast');
  let toastTimer;
  function say(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 2600);
  }

  /* =========================================================
     The room: things to find
     ========================================================= */
  const dialog = document.getElementById('story');
  const body = document.getElementById('story-body');
  function openPanel(html) {
    body.innerHTML = html;
    if (typeof dialog.showModal === 'function') { if (!dialog.open) dialog.showModal(); }
    else dialog.setAttribute('open', '');
    dialog.querySelector('.story-inner').scrollTop = 0;
  }
  const panel = (kicker, title, html) => `<p class="mono kicker">${kicker}</p><h3 id="story-title">${title}</h3>${html}`;
  const rows = (list) => `<ul class="rows">${list.map((r) => `<li><div class="row"><b>${r[0]}</b><span>${r[1]}</span><i class="mono">${r[2] || ''}</i></div></li>`).join('')}</ul>`;
  const go = (href, label) => `<a class="ghost" href="${href}">${label}</a>`;
  const chips = (list) => `<div class="chips">${list.map((c, i) => `<span class="chip ${['c-blue','c-pink','c-green','c-yellow','c-lilac'][i % 5]}">${c}</span>`).join('')}</div>`;
  // your email and résumé come from site.json (the build puts them on <body>)
  const EMAIL = document.body.dataset.email || 'hello@yourname.com';
  const RESUME = document.body.dataset.resume || '';
  const el = (id) => document.getElementById('o-' + id);
  const replay = (node, cls) => { node.classList.remove(cls); void node.getBoundingClientRect(); node.classList.add(cls); };

  // Everything you can find in the room, Edit the text here.
  const THINGS = {
    // the books lead straight to the About page
    books: { label: 'About me', act: () => { window.location.href = 'about.html'; } },
    // the monitor and the sketchbook lead straight to their pages
    monitor: { label: 'My work', act: () => { window.location.href = 'work.html'; } },
    sketch: { label: 'How I work', act: () => { window.location.href = 'notes.html'; } },
    calendar: { label: 'Experience', open: () => panel('On the calendar', 'Experience',
      `${rows([['[Role] · [Company]', '[What you did there, in one line.]', '[2024 — now]'], ['[Role] · [Company]', '[What you did there, in one line.]', '[2022 — 24]'], ['[Role] · [Company]', '[What you did there, in one line.]', '[2020 — 22]']])}
      <div class="panel-actions">${RESUME ? `<a class="ghost" href="${RESUME}" target="_blank" rel="noopener">Download résumé (PDF)</a>` : `<a class="ghost" href="#" data-todo="Add your résumé link in site.json ✿">Download résumé (PDF)</a>`}</div>`) },
    diploma: { label: 'Where I studied', open: () => panel('Framed on the shelf', 'Where I <em>studied</em>',
      rows([['[Degree]', '[School, City]', '[Years]'], ['[Course or certificate]', '[Where]', '[Year]']])) },
    certificate: { label: 'Japanese, level N4', open: () => panel('Framed on the wall', 'Japanese, <em>level N4</em>',
      `<p class="lead">[A line about learning Japanese: why you started, and what it opened up for you.]</p>
      <figure class="cert-photo"><img src="assets/n4-certificate.jpg" alt="Japanese-Language Proficiency Test certificate, level N4, January 2025" loading="lazy"></figure>
      ${rows([['Japanese-Language Proficiency Test', 'Level N4 · The Japan Foundation & JEES', '2025']])}`) },
    trophy: { label: 'Kind words',
      // first click switches the award's RGB light on (the crystal turns); next click opens the panel
      act: () => {
        const aw = el('trophy');
        if (!aw.classList.contains('on')) { setAward(true); say('Good Job Award, lit up ✿ click again for the kind words'); }
        else openPanel(THINGS.trophy.open());
      },
      open: () => panel('The crystal award', 'Kind <em>words</em>',
      `<p class="lead">A Good Job Award from my company, for editing our product catalogue. [One sentence on the project and what you are proud of.]</p>
      ${rows([['Good Job Award', 'For catalogue editing · [Company]', '[Year]']])}
      <p class="quote">“[A short quote from a teammate or client about working with you.]”</p><p class="mono quote-by">[Name] · [Role, Company]</p>
      <p class="quote">“[Another one. Specific beats glowing.]”</p><p class="mono quote-by">[Name] · [Role, Company]</p>
      <div class="panel-actions"><button class="ghost" type="button" data-award-off>Switch the award light off</button></div>`) },
    bouquet: { label: 'A thank-you bouquet', open: () => panel('On the desk', 'A thank-you <em>bouquet</em>',
      `<p class="lead">[A short story about this bouquet: who gave it, and what the moment meant to you.]</p>
      <p class="quote">“[A line from the card that came with it.]”</p><p class="mono quote-by">[From whom] · [When]</p>
      <p>[What you learned from mentoring, teaching or working with them, in a sentence or two.]</p>`) },
    map: { label: "Where I've been", open: () => panel('Pinned to the wall', "Where I've <em>been</em>",
      `<p class="lead">[Places that shaped how you see things.]</p>
      ${rows([['[City, Country]', '[What you were doing there]', '[Year]'], ['[City, Country]', '[What you were doing there]', '[Year]'], ['[City, Country]', '[What you were doing there]', '[Year]']])}`) },
    phone: { label: 'Say hello', open: () => panel('Ring ring', 'Say <em>hello</em>',
      `<p class="lead">I'm always happy to talk about new projects, ideas, or just say hi.</p>
      <div class="panel-actions"><a class="pill" href="mailto:${EMAIL}" data-copy="${EMAIL}">${EMAIL} <span aria-hidden="true">↗</span></a>
      <a class="ghost" href="#">LinkedIn</a><a class="ghost" href="#">Instagram</a><a class="ghost" href="#">Dribbble</a></div>
      <p class="mono copy-hint" style="margin-top:14px">click the email to copy it</p>`) },
    record: { label: 'On repeat',
      // first click drops the needle (the record spins, notes float up); next click opens the playlist
      act: () => {
        const r = el('record');
        if (!r.classList.contains('playing')) { r.classList.add('playing'); say('Now playing ♪ click again for the playlist'); }
        else openPanel(THINGS.record.open());
      },
      open: () => panel('On the record player', 'On <em>repeat</em>',
      `<p class="lead">What's playing while I work.</p>
      ${rows([['[Song]', '[Artist]', '[Genre]'], ['[Song]', '[Artist]', '[Genre]'], ['[Song]', '[Artist]', '[Genre]']])}
      <div class="panel-actions"><button class="ghost" type="button" data-record-stop>Stop the record</button></div>`) },
    guitar: { label: 'After hours', open: () => panel('Leaning on the wall', 'After <em>hours</em>',
      `<p class="lead">[What you do when you're not working: a hobby, a craft, a sport.]</p>
      ${chips(['[Guitar]', '[Hiking]', '[Film photos]', '[Baking]'])}
      <p>[One small story about it. Why you love it, or what it taught you about your work.]</p>`) },
    mug: { label: 'Fuel', open: () => panel('The pink mug', '<em>Fuel</em>',
      `<p class="lead">Currently powered by [your coffee or tea order].</p>
      ${rows([['Fun fact', '[Something surprising about you.]', '01'], ['Fun fact', '[Something you are weirdly good at.]', '02']])}`) },
    window: { label: 'A peek outside', open: () => panel('Through the window', 'A peek <em>outside</em>',
      `<p class="lead">Out there is the meadow where my story happens: how I started, the moment things turned, and the work that came out of it.</p>
      <p>Tip: the wall clock changes the time of day. Try it at golden hour.</p>
      <div class="panel-actions">${go('about.html', 'Step outside →')}</div>`) },
    lamp: { label: 'Switch the lamp', act: () => {
      lampOn = !lampOn; setLamp();
      try { localStorage.setItem('lamp', lampOn ? 'on' : 'off'); } catch (e) {}
      say(lampOn ? 'Lamp on ✿' : 'Lamp off'); } },
    clock: { label: 'Change the time of day', act: () => {
      const n = nextPreset(); tweenTo(n); say(`Skipping ahead to ${phaseName(n)} ✿`); } },
    plant: { label: 'Water the plant', act: () => { replay(el('plant'), 'watered'); say('The monstera says thank you ✿'); } },
  };

  /* the crystal award: a 4-sided glass block that turns on its LED base */
  const CRY = { cx: 350, w: 28, d: 12, top: 452, bot: 502, k: 0.14, rest: -0.42 };
  const cryFaces = [...document.querySelectorAll('#crystal3d .cf')];
  const cryTop = document.getElementById('award-top');
  const cryTint = document.getElementById('award-tint');
  const cryEtch = document.getElementById('award-etch');
  const corners = [[-CRY.w / 2, -CRY.d / 2], [CRY.w / 2, -CRY.d / 2], [CRY.w / 2, CRY.d / 2], [-CRY.w / 2, CRY.d / 2]];
  const sides = [{ i: [3, 2], n: [0, 1] }, { i: [2, 1], n: [1, 0] }, { i: [1, 0], n: [0, -1] }, { i: [0, 3], n: [-1, 0] }];
  function drawCrystal(t) {
    const c = Math.cos(t), sn = Math.sin(t);
    const P = corners.map(([x, z]) => ({ x: CRY.cx + x * c + z * sn, z: -x * sn + z * c }));
    const order = sides.map((f) => ({
      f, nz: -f.n[0] * sn + f.n[1] * c, nx: f.n[0] * c + f.n[1] * sn,
      zc: (P[f.i[0]].z + P[f.i[1]].z) / 2,
    })).sort((a, b) => a.zc - b.zc);
    order.forEach((o, idx) => {
      const a = P[o.f.i[0]], b = P[o.f.i[1]], face = cryFaces[idx];
      const yt = (q) => (CRY.top + q.z * CRY.k).toFixed(1), yb = (q) => (CRY.bot + q.z * CRY.k).toFixed(1);
      face.setAttribute('points', `${a.x.toFixed(1)},${yt(a)} ${b.x.toFixed(1)},${yt(b)} ${b.x.toFixed(1)},${yb(b)} ${a.x.toFixed(1)},${yb(a)}`);
      const front = o.nz > 0, lit = Math.max(0, o.nx * -0.55 + o.nz * 0.83);
      face.setAttribute('fill', mix('#B3C9D8', '#F7FBFE', front ? 0.35 + 0.65 * lit : 0.2));
      face.setAttribute('fill-opacity', front ? 0.62 : 0.3);
      face.setAttribute('stroke-opacity', front ? 0.9 : 0.25);
    });
    cryTop.setAttribute('points', P.map((q) => `${q.x.toFixed(1)},${(CRY.top + q.z * CRY.k).toFixed(1)}`).join(' '));
    const xs = P.map((q) => q.x), x0 = Math.min(...xs).toFixed(1), x1 = Math.max(...xs).toFixed(1);
    cryTint.setAttribute('points', `${x0},${CRY.top} ${x1},${CRY.top} ${x1},${CRY.bot} ${x0},${CRY.bot}`);
    cryEtch.setAttribute('transform', `translate(${CRY.cx} 0) scale(${c.toFixed(3)} 1) translate(${-CRY.cx} 0)`);
  }
  const spin = { a: CRY.rest, on: false, raf: 0, last: 0 };
  function spinLoop(now) {
    const dt = Math.min(50, now - (spin.last || now));
    spin.last = now;
    if (spin.on) spin.a += dt * 0.0009;            // about one turn every 7 seconds
    else {                                         // ease forward to the resting angle, then stop
      const target = CRY.rest + Math.ceil((spin.a - CRY.rest) / (2 * Math.PI) - 1e-6) * 2 * Math.PI;
      const left = target - spin.a;
      if (left < 0.004) { spin.a = CRY.rest; drawCrystal(spin.a); spin.raf = 0; spin.last = 0; return; }
      spin.a += Math.min(left, Math.max(0.0003 * dt, left * 0.06));
    }
    drawCrystal(spin.a);
    spin.raf = requestAnimationFrame(spinLoop);
  }
  function setAward(on) {
    el('trophy').classList.toggle('on', on);
    hero.classList.toggle('award-on', on);
    spin.on = on && !reduceMotion;
    if (!spin.raf && !reduceMotion) spin.raf = requestAnimationFrame(spinLoop);
  }
  const objs = room ? [...room.querySelectorAll('.obj')] : [];

  function activate(id) {
    const t = THINGS[id];
    if (!t) return;
    if (t.act) t.act(); else openPanel(t.open());
  }
  objs.forEach((o) => {
    o.addEventListener('click', () => activate(o.dataset.id));
    o.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(o.dataset.id); }
    });
  });

  // labels that follow the cursor
  const tip = document.getElementById('tip');
  if (finePointer && room) {
    room.addEventListener('pointermove', (e) => {
      const o = e.target.closest('.obj');
      if (!o) { tip.classList.remove('on'); return; }
      tip.textContent = THINGS[o.dataset.id].label;
      tip.style.transform = `translate(${e.clientX + 16}px, ${e.clientY + 16}px)`;
      tip.classList.add('on');
    });
    room.addEventListener('pointerleave', () => tip.classList.remove('on'));
    window.addEventListener('scroll', () => tip.classList.remove('on'), { passive: true });
  }

  // on phones the room is wider than the screen: start in the middle, swipe to look around
  const pan = document.getElementById('room-pan');
  let panW = 0;
  const centerPan = () => {
    if (!pan || pan.clientWidth === panW) return;
    panW = pan.clientWidth;
    pan.scrollLeft = (pan.scrollWidth - pan.clientWidth) / 2;
  };
  centerPan();
  window.addEventListener('resize', centerPan);

  /* ---------- Wall calendar: this month, with today circled ---------- */
  (function fillCalendar() {
    const g = document.getElementById('cal-days');
    if (!g) return;
    const now = new Date();
    const y = now.getFullYear(), m = now.getMonth();
    const names = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.'];
    document.getElementById('cal-mnum').textContent = String(m + 1).padStart(2, '0');
    document.getElementById('cal-mname').textContent = names[m];
    const first = (new Date(y, m, 1).getDay() + 6) % 7; // weeks start on Monday
    const total = new Date(y, m + 1, 0).getDate();
    const rows = Math.ceil((first + total) / 7);
    const x = (c) => (1070.5 + c * 7.6).toFixed(1);
    const top = rows > 5 ? 355.5 : 357;
    const step = rows > 5 ? 6.3 : 7.4;
    let out = ['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, c) => `<text x="${x(c)}" y="349" class="svg-calhead${c > 4 ? ' wk' : ''}">${d}</text>`).join('');
    for (let d = 1; d <= total; d++) {
      const i = first + d - 1, c = i % 7, r = Math.floor(i / 7);
      const cy = top + r * step;
      if (d === now.getDate()) out += `<circle cx="${x(c)}" cy="${(cy - 1.4).toFixed(1)}" r="3.1" fill="none" stroke="#3A57C4" stroke-width=".7"/>`;
      out += `<text x="${x(c)}" y="${cy.toFixed(1)}" class="svg-calday${c > 4 ? ' wk' : ''}">${d}</text>`;
    }
    g.innerHTML = out;
  })();

  /* ---------- Cursor depth: the view outside the window shifts ---------- */
  if (hero && finePointer && !reduceMotion) {
    hero.addEventListener('pointermove', (e) => {
      const r = hero.getBoundingClientRect();
      hero.style.setProperty('--mx', (((e.clientX - r.left) / r.width) * 2 - 1).toFixed(3));
      hero.style.setProperty('--my', (((e.clientY - r.top) / r.height) * 2 - 1).toFixed(3));
    });
    hero.addEventListener('pointerleave', () => { hero.style.setProperty('--mx', 0); hero.style.setProperty('--my', 0); });
  }

  /* ---------- Scroll: parallax, quote ---------- */
  const layers = hero ? hero.querySelectorAll('[data-speed]') : [];
  const pull = document.getElementById('pull');

  // split the quote into words that light up as you read
  function splitWords(node) {
    [...node.childNodes].forEach((child) => {
      if (child.nodeType === 3) {
        const frag = document.createDocumentFragment();
        child.textContent.split(/(\s+)/).forEach((part) => {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          const s = document.createElement('span');
          s.className = 'w';
          s.textContent = part;
          frag.appendChild(s);
        });
        child.replaceWith(frag);
      } else if (child.nodeType === 1) splitWords(child);
    });
  }
  if (pull) splitWords(pull);
  const words = pull ? pull.querySelectorAll('.w') : [];

  function onScroll() {
    const y = window.scrollY;
    if (hero && !reduceMotion) {
      const hy = Math.min(y, hero.offsetHeight);
      layers.forEach((el) => { el.style.transform = `translate3d(0, ${(hy * parseFloat(el.dataset.speed)).toFixed(1)}px, 0)`; });
    }
    if (!pull) return;
    const q = pull.getBoundingClientRect();
    const prog = clamp((window.innerHeight * 0.9 - q.top) / (window.innerHeight * 0.5));
    const lit = Math.round(prog * words.length);
    words.forEach((w, i) => w.classList.toggle('lit', i < lit));
  }
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();

  /* ---------- Postcards: one per project ---------- */
  const list = document.getElementById('postcards');
  const tilts = [-0.8, 1.4, -1.6, 1.1, -1.2, 1.6];
  // a round postmark with the year, plus wavy cancellation lines
  const postmark = (year) => `
    <svg class="pc-postmark" viewBox="0 0 150 80" aria-hidden="true">
      <g fill="none" stroke="currentColor" stroke-width="1.6">
        <circle cx="110" cy="40" r="30"/><circle cx="110" cy="40" r="24" stroke-width=".8"/>
        <path d="M2 26 q9 -6 18 0 t18 0 t18 0 t18 0 M2 40 q9 -6 18 0 t18 0 t18 0 t18 0 M2 54 q9 -6 18 0 t18 0 t18 0 t18 0"/>
      </g>
      <text x="110" y="36" text-anchor="middle" class="pm-small">POSTED</text>
      <text x="110" y="51" text-anchor="middle" class="pm-year">${year}</text>
    </svg>`;
  if (list) projects.forEach((p, i) => {
    const li = document.createElement('li');
    li.className = 'pc-item reveal' + (i === 0 ? ' feature' : '');
    li.style.setProperty('--tilt', tilts[i % tilts.length] + 'deg');
    li.style.transitionDelay = (i * 90) + 'ms';
    const icon = `<svg viewBox="0 0 100 100" aria-hidden="true">${icons[p.icon]}</svg>`;
    li.innerHTML = `
      <button class="postcard" type="button" data-i="${i}" aria-label="Read the story of ${p.title}">
        <span class="pc-front" style="--art:${p.art}">
          ${p.cover
            ? `<img class="pc-img" src="${p.cover}" alt="" loading="lazy">`
            : `<span class="pc-icon">${icon}</span><span class="pc-cover mono">cover image</span>`}
        </span>
        <span class="pc-back">
          <span class="pc-stamp" style="--art:${p.art}"><span class="pc-stamp-in">${icon}</span></span>
          ${postmark(p.year)}
          <span class="pc-no mono">No. ${String(i + 1).padStart(2, '0')}${i === 0 ? ' · Featured' : ''}</span>
          <span class="pc-title">${p.title}</span>
          <span class="pc-sum">${p.summary}</span>
          <span class="pc-lines">
            <span><b class="mono">Type</b>${p.tag}</span>
            <span><b class="mono">Journey</b>${p.dur} · ${p.year}</span>
          </span>
          <span class="pc-read hand">read the story <span aria-hidden="true">→</span></span>
        </span>
      </button>`;
    list.appendChild(li);
  });

  function openProject(i) {
    const p = projects[i];
    openPanel(`
      <p class="mono kicker">Project ${String(i + 1).padStart(2, '0')} · ${p.year}</p>
      <h3 id="story-title">${p.title}</h3>
      <p class="summary">${p.summary}</p>
      <div class="facts mono"><span>${p.tag}</span><span>${p.dur} journey</span><span>[Your role]</span><span>[Team]</span></div>
      <div class="cover" style="background:${p.art}"><span class="mono">hero image here</span></div>
      <ol class="beats">${beats.map((b, j) => `<li data-n="${j + 1}"><h4>${b[0]}</h4><p>${b[1]}</p></li>`).join('')}</ol>`);
  }
  list?.addEventListener('click', (e) => {
    const btn = e.target.closest('.postcard');
    if (btn) openProject(+btn.dataset.i);
  });
  dialog?.addEventListener('click', (e) => {
    if (e.target === dialog || e.target.closest('[data-close]')) { dialog.close(); return; }
    if (e.target.closest('[data-record-stop]')) { el('record').classList.remove('playing'); dialog.close(); say('Record stopped'); return; }
    if (e.target.closest('[data-award-off]')) { setAward(false); dialog.close(); say('Award light off'); return; }
    const link = e.target.closest('a[href^="#"]');
    if (link && link.getAttribute('href').length > 1) dialog.close();
  });

  /* ---------- Reveal on scroll ---------- */
  const revealIO = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('in'); revealIO.unobserve(e.target); }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('.reveal').forEach((el) => revealIO.observe(el));

  /* ---------- Draggable desk notes ---------- */
  const board = document.getElementById('board');
  const canDrag = window.matchMedia('(min-width: 901px)');
  let z = 10;
  board?.querySelectorAll('.item').forEach((item) => {
    item.addEventListener('pointerdown', (e) => {
      if (!canDrag.matches) return;
      e.preventDefault();
      const b = board.getBoundingClientRect();
      const start = { x: e.clientX, y: e.clientY, left: item.offsetLeft, top: item.offsetTop };
      item.setPointerCapture(e.pointerId);
      item.classList.add('dragging');
      item.style.zIndex = ++z;
      const move = (ev) => {
        item.style.left = Math.max(-20, Math.min(b.width - item.offsetWidth + 20, start.left + ev.clientX - start.x)) + 'px';
        item.style.top = Math.max(-20, Math.min(b.height - item.offsetHeight + 20, start.top + ev.clientY - start.y)) + 'px';
      };
      const up = () => {
        item.classList.remove('dragging');
        item.removeEventListener('pointermove', move);
        item.removeEventListener('pointerup', up);
        item.removeEventListener('pointercancel', up);
      };
      item.addEventListener('pointermove', move);
      item.addEventListener('pointerup', up);
      item.addEventListener('pointercancel', up);
    });
  });

  /* ---------- Copy email (anything with data-copy), placeholders (data-todo) ---------- */
  document.addEventListener('click', (e) => {
    const todo = e.target.closest('[data-todo]');
    if (todo) { e.preventDefault(); say(todo.dataset.todo); return; }
    const c = e.target.closest('[data-copy]');
    if (!c || !navigator.clipboard) return; // no clipboard: let the mailto link work
    e.preventDefault();
    navigator.clipboard.writeText(c.dataset.copy)
      .then(() => say('Email copied ✿'))
      .catch(() => { window.location.href = c.href; });
  });

  /* ---------- Contact letter: date it, then post it as an email draft ---------- */
  const letter = document.getElementById('letter');
  if (letter) {
    const today = document.getElementById('today');
    if (today) today.textContent = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
    letter.addEventListener('submit', (e) => {
      e.preventDefault();
      const why = (letter.querySelector('input[name="why"]:checked') || {}).value || 'saying hi';
      const msg = letter.querySelector('#letter-msg').value.trim();
      const from = letter.querySelector('#letter-from').value.trim();
      const body = `Hi,\n\nI'd love to talk about ${why}.\n\n${msg ? msg + '\n\n' : ''}Warmly,\n${from}`;
      const subject = `Hello: ${why}${from ? ' (from ' + from + ')' : ''}`;
      window.location.href = `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
      say('Opening your email app ✿');
    });
  }

  /* ---------- Soft cursor ring ---------- */
  const ring = document.querySelector('.ring');
  if (finePointer && !reduceMotion) {
    let tx = 0, ty = 0, x = 0, y = 0;
    window.addEventListener('pointermove', (e) => {
      tx = e.clientX; ty = e.clientY;
      ring.classList.add('on');
      ring.classList.toggle('big', !!e.target.closest('a, button, label, .postcard, .item, .obj'));
    });
    document.addEventListener('pointerleave', () => ring.classList.remove('on'));
    (function loop() {
      x += (tx - x) * 0.18; y += (ty - y) * 0.18;
      ring.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
      requestAnimationFrame(loop);
    })();
  }

  const yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
})();
