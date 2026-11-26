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
    window.RoomSound?.setDaytime(daytime);
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
  function reopenPanel() {
    if (typeof dialog.showModal === 'function') { if (!dialog.open) dialog.showModal(); }
    else dialog.setAttribute('open', '');
  }
  function openPanel(html) {
    if (body.querySelector('.embed-frame')) { deckState.external = false; el('record')?.classList.remove('playing'); }  // the embedded player goes with the old panel
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
  let SOCIALS = {};  // { LinkedIn: 'https://…' }, only the ones filled in
  try { SOCIALS = JSON.parse(document.body.dataset.socials || '{}'); } catch (e) {}
  const el = (id) => document.getElementById('o-' + id);
  const replay = (node, cls) => { node.classList.remove(cls); void node.getBoundingClientRect(); node.classList.add(cls); };

  /* ---------- The playlist on the record player: edit these ----------
     len is the track length (m:ss). The "Listen" button uses "playlist" in site.json. */
  const PLAYLIST = {
    title: 'Desk sessions', volume: 'Vol. 01',
    sides: [
      { name: 'Side A', tracks: [
        { title: '[Song title]', artist: '[Artist]', len: '3:42', mood: '[Genre]', note: '[Why this one is on repeat, in one line.]' },
        { title: '[Song title]', artist: '[Artist]', len: '4:05', mood: '[Genre]', note: '[What you are usually doing when it plays.]' },
        { title: '[Song title]', artist: '[Artist]', len: '2:58', mood: '[Genre]', note: '[A memory it brings back.]' },
      ] },
      { name: 'Side B', tracks: [
        { title: '[Song title]', artist: '[Artist]', len: '5:11', mood: '[Genre]', note: '[The one for deep focus.]' },
        { title: '[Song title]', artist: '[Artist]', len: '3:27', mood: '[Genre]', note: '[The one for a slow Sunday.]' },
        { title: '[Song title]', artist: '[Artist]', len: '4:33', mood: '[Genre]', note: '[The one you never skip.]' },
      ] },
    ],
  };
  const PLAYLIST_URL = document.body.dataset.playlist || '';
  // A real playlist from site.json ("playlist"): a Spotify, YouTube or Apple Music link becomes
  // that service's official player. Nothing loads from them until the visitor asks for it.
  function embedFor(url) {
    let u;
    try { u = new URL(url); } catch (e) { return null; }
    const host = u.hostname.replace(/^www\./, '');
    if (host === 'open.spotify.com') {
      const m = u.pathname.match(/\/(playlist|album|track|artist)\/([A-Za-z0-9]+)/);
      if (m) return { name: 'Spotify', src: `https://open.spotify.com/embed/${m[1]}/${m[2]}?utm_source=generator`, kind: 'spotify' };
    }
    if (host === 'youtube.com' || host === 'music.youtube.com' || host === 'm.youtube.com') {
      const list = u.searchParams.get('list');
      if (list && /^[A-Za-z0-9_-]+$/.test(list)) return { name: 'YouTube', src: `https://www.youtube-nocookie.com/embed/videoseries?list=${list}`, kind: 'youtube' };
    }
    if (host === 'music.apple.com' && /^\/[a-z]{2}\/(playlist|album)\//.test(u.pathname)) {
      return { name: 'Apple Music', src: `https://embed.music.apple.com${u.pathname}`, kind: 'apple' };
    }
    return null;
  }
  const EMBED = PLAYLIST_URL ? embedFor(PLAYLIST_URL) : null;
  const TRACKS = PLAYLIST.sides.flatMap((side) => side.tracks);
  const secs = (len) => { const [m, s2] = len.split(':').map(Number); return m * 60 + (s2 || 0); };
  const mmss = (t) => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;
  const ICON = {
    prev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 6v12M18 6l-8 6 8 6z"/></svg>',
    next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17 6v12M6 6l8 6-8 6z"/></svg>',
    play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l10.5-6.5z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13M16 5.5v13"/></svg>',
  };
  const eq = '<span class="eq" aria-hidden="true"><i></i><i></i><i></i><i></i></span>';

  function deckHTML() {
    let n = 0;
    const sides = PLAYLIST.sides.map((side) => `
      <div class="side">
        <p class="mono side-name">${side.name}</p>
        <ol class="tracks">${side.tracks.map((t) => { const i = n++; return `
          <li><button class="track" type="button" data-track="${i}">
            <span class="tn mono"><span class="num">${String(i + 1).padStart(2, '0')}</span>${eq}</span>
            <span class="tt"><b>${t.title}</b><span>${t.artist}</span></span>
            <span class="tg mono">${t.mood}</span>
            <span class="tl mono">${t.len}</span>
          </button></li>`; }).join('')}</ol>
      </div>`).join('');
    const listen = PLAYLIST_URL
      ? `<a class="ghost" href="${PLAYLIST_URL}" target="_blank" rel="noopener">Open in ${EMBED ? EMBED.name : 'a new tab'} ↗</a>`
      : `<a class="ghost" href="#" data-todo="Add your playlist link in site.json ✿">Listen to the playlist ↗</a>`;
    const mine = EMBED ? `
      <div class="deck-tabs" role="tablist" aria-label="What to play">
        <button class="deck-tab" type="button" role="tab" id="tab-mine" aria-controls="pane-mine" aria-selected="true" data-tab="mine">My playlist</button>
        <button class="deck-tab" type="button" role="tab" id="tab-radio" aria-controls="pane-radio" aria-selected="false" data-tab="radio">Room radio</button>
      </div>
      <div class="deck-pane" id="pane-mine" role="tabpanel" aria-labelledby="tab-mine">
        <div class="embed-slot embed-${EMBED.kind}" id="embed-slot">${embedCover()}</div>
      </div>` : '';
    return `
      <p class="lead">${EMBED ? 'Soft, calm and mostly instrumental: what plays while I work.' : "What's playing while I work. Pick a track."}</p>
      ${mine}
      <div class="deck-pane" id="pane-radio" role="tabpanel"${EMBED ? ' aria-labelledby="tab-radio" hidden' : ''}>
      ${EMBED ? '<p class="radio-note">The room\'s own tunes: soft lo-fi made right here in your browser.</p>' : ''}
      <div class="deck" id="deck">
        <div class="sleeve" aria-hidden="true">
          <div class="disc"><span class="disc-label"><i></i></span></div>
          <div class="sleeve-art">
            <span class="mono sleeve-vol">${PLAYLIST.volume}</span>
            <b class="sleeve-title">${PLAYLIST.title.replace(/ (\S+)$/, ' <em>$1</em>')}</b>
            <span class="sleeve-sun"></span><span class="sleeve-hill"></span><span class="sleeve-hill h2"></span>
          </div>
        </div>
        <div class="np" aria-live="polite">
          <p class="mono np-kicker">${eq}<span class="np-state">Now playing</span></p>
          <p class="np-title"></p>
          <p class="np-artist"></p>
          <p class="np-note hand"></p>
          <div class="bar" aria-hidden="true"><span class="bar-fill"></span></div>
          <div class="times mono"><span class="t-now">0:00</span><span class="t-len">0:00</span></div>
          <div class="controls">
            <button class="ctl" type="button" data-deck="prev" aria-label="Previous track">${ICON.prev}</button>
            <button class="ctl play" type="button" data-deck="play" aria-label="Pause">${ICON.pause}</button>
            <button class="ctl" type="button" data-deck="next" aria-label="Next track">${ICON.next}</button>
          </div>
        </div>
      </div>
      <div class="sides">${sides}</div>
      </div>
      <div class="panel-actions">${listen}</div>`;
  }
  function embedCover() {
    return `
      <div class="embed-cover">
        <div class="embed-sleeve" aria-hidden="true"><span class="embed-disc"></span><span class="embed-note">♪</span></div>
        <div class="embed-copy">
          <p class="mono embed-kicker">My playlist · ${EMBED.name}</p>
          <p class="embed-title">Music I keep on <em>repeat</em></p>
          <p class="embed-help">Plays through ${EMBED.name}'s own player${EMBED.kind === 'youtube' ? '' : '. Visitors hear previews unless they\'re signed in'}.</p>
          <button class="pill embed-load" type="button" data-embed="load">Load the player <span aria-hidden="true">▶</span></button>
        </div>
      </div>`;
  }

  // The record keeps time whenever it's spinning, panel open or not, and moves on to the next
  // track at the end. Playing and pausing also start and stop the music (sound.js).
  const deckState = { i: 0, t: 0 };
  const recordPlaying = () => !!el('record')?.classList.contains('playing');
  function renderDeck() {
    const deck = document.getElementById('deck');
    if (!deck) return;
    const q = (sel) => deck.querySelector(sel);
    const tr = TRACKS[deckState.i], len = secs(tr.len), on = recordPlaying() && !deckState.external;
    deck.classList.toggle('playing', on);
    q('.np-title').textContent = tr.title;
    q('.np-artist').textContent = tr.artist;
    q('.np-note').textContent = tr.note;
    q('.np-state').textContent = on ? 'Now playing' : 'Paused';
    q('.t-now').textContent = mmss(deckState.t);
    q('.t-len').textContent = tr.len;
    q('.bar-fill').style.width = (100 * deckState.t / len).toFixed(2) + '%';
    const play = q('[data-deck="play"]');
    play.innerHTML = on ? ICON.pause : ICON.play;
    play.setAttribute('aria-label', on ? 'Pause' : 'Play');
    body.querySelectorAll('.track').forEach((b) => {
      const cur = +b.dataset.track === deckState.i;
      b.classList.toggle('current', cur);
      if (cur) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
    });
    body.querySelector('.sides')?.classList.toggle('playing', on);
  }
  function setRecord(on) {
    if (on) unloadEmbed();  // the room radio takes over from the embedded player
    deckState.external = false;
    el('record')?.classList.toggle('playing', on);
    if (on) window.RoomSound?.playMusic(deckState.i); else window.RoomSound?.pauseMusic();
    renderDeck();
  }
  function loadEmbed() {
    const slot = document.getElementById('embed-slot');
    if (!slot || !EMBED) return;
    const f = document.createElement('iframe');
    f.className = 'embed-frame';
    f.src = EMBED.src;
    f.title = `My playlist on ${EMBED.name}`;
    f.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    slot.replaceChildren(f);
    slot.classList.add('loaded');
    // the record keeps spinning, but the room radio goes quiet so the two never play at once
    deckState.external = true;
    window.RoomSound?.pauseMusic();
    el('record')?.classList.add('playing');
    renderDeck();
    say(`Press play in the ${EMBED.name} player ♪`);
  }
  function unloadEmbed() {
    const slot = document.getElementById('embed-slot');
    if (slot?.classList.contains('loaded')) { slot.classList.remove('loaded'); slot.innerHTML = embedCover(); }
  }
  function showTab(name) {
    body.querySelectorAll('.deck-tab').forEach((t) => t.setAttribute('aria-selected', t.dataset.tab === name ? 'true' : 'false'));
    body.querySelectorAll('.deck-pane').forEach((p) => { p.hidden = p.id !== 'pane-' + name; });
  }
  function deckGo(i) {
    deckState.i = (i + TRACKS.length) % TRACKS.length;
    deckState.t = 0;
    setRecord(true);
  }
  if (el('record')) setInterval(() => {
    if (!recordPlaying() || deckState.external) return;
    deckState.t += 1;
    if (deckState.t >= secs(TRACKS[deckState.i].len)) deckGo(deckState.i + 1);
    else renderDeck();
  }, 1000);
  function startDeck() {
    if (!document.getElementById('deck')) return;
    body.onclick = (e) => {
      const tab = e.target.closest('.deck-tab');
      if (tab) { showTab(tab.dataset.tab); return; }
      if (e.target.closest('[data-embed="load"]')) { loadEmbed(); return; }
      const tb = e.target.closest('.track');
      if (tb) { deckGo(+tb.dataset.track); return; }
      const c = e.target.closest('[data-deck]');
      if (!c) return;
      if (c.dataset.deck === 'prev') deckGo(deckState.t > 3 ? deckState.i : deckState.i - 1);  // like a real player: restart, then go back
      if (c.dataset.deck === 'next') deckGo(deckState.i + 1);
      if (c.dataset.deck === 'play') { const on = !(recordPlaying() && !deckState.external); setRecord(on); say(on ? 'Playing ♪' : 'Paused'); }
    };
    renderDeck();
  }
  dialog?.addEventListener('close', () => { body.onclick = null; });

  /* ---------- Where I've been: a hand-drawn map of Asia with a pin per place ----------
     Edit the places here. lat / lon put the pin on the map (look a city up on any map site);
     flag is the emoji, and code picks the drawn flag used where emoji flags don't show.
     city, doing and year are optional: leave them '' and the card simply skips them. */
  const PLACES = [
    { name: 'Singapore', flag: '🇸🇬', code: 'sg', region: 'Southeast Asia', lat: 1.35, lon: 103.82, city: '', doing: '', year: '' },
    { name: 'Thailand', flag: '🇹🇭', code: 'th', region: 'Southeast Asia', lat: 13.75, lon: 100.5, city: '', doing: '', year: '' },
    { name: 'Malaysia', flag: '🇲🇾', code: 'my', region: 'Southeast Asia', lat: 3.6, lon: 101.6, city: '', doing: '', year: '' },
    { name: 'Vietnam', flag: '🇻🇳', code: 'vn', region: 'Southeast Asia', lat: 21.03, lon: 105.85, city: '', doing: '', year: '' },
    { name: 'Japan', flag: '🇯🇵', code: 'jp', region: 'East Asia', lat: 35.68, lon: 139.7, city: '', doing: '', year: '' },
    { name: 'Philippines', flag: '🇵🇭', code: 'ph', region: 'Southeast Asia', lat: 14.6, lon: 121, city: '', doing: '', year: '' },
    { name: 'India', flag: '🇮🇳', code: 'in', region: 'South Asia', lat: 28.6, lon: 77.2, city: '', doing: '', year: '' },
  ];
  const HOME = { label: document.body.dataset.home || 'Home', lat: 11.56, lon: 104.92 };

  // Flags: the real emoji where the device can show them (Mac, iPhone, Android), and small
  // drawn flags elsewhere (Windows shows flag emoji as two letters, like "JP").
  const canShowFlagEmoji = (() => {
    try {
      const c = document.createElement('canvas'); c.width = c.height = 24;
      const x = c.getContext('2d'); x.textBaseline = 'top'; x.font = '20px sans-serif'; x.fillText('🇯🇵', 0, 0);
      const d = x.getImageData(0, 0, 24, 24).data;
      for (let i = 0; i < d.length; i += 4) if (d[i + 3] > 100 && d[i] > 150 && d[i + 1] < 90 && d[i + 2] < 90) return true;  // found Japan's red sun
    } catch (e) {}
    return false;
  })();
  const star = (cx, cy, r, fill) => {
    let d = '';
    for (let k = 0; k < 10; k++) {
      const a = -Math.PI / 2 + k * Math.PI / 5, rr = k % 2 ? r * .42 : r;
      d += (k ? 'L' : 'M') + (cx + rr * Math.cos(a)).toFixed(2) + ' ' + (cy + rr * Math.sin(a)).toFixed(2);
    }
    return `<path d="${d}Z" fill="${fill}"/>`;
  };
  const FLAG_ART = {  // drawn on a 30 x 20 grid
    sg: '<rect width="30" height="10" fill="#EF3340"/><rect y="10" width="30" height="10" fill="#fff"/><circle cx="7" cy="5" r="3.4" fill="#fff"/><circle cx="8.5" cy="5" r="3.2" fill="#EF3340"/>'
      + [[11, 2.6], [13.2, 4.2], [12.4, 6.8], [9.6, 6.8], [8.8, 4.2]].map(([x, y]) => star(x, y, .9, '#fff')).join(''),
    th: '<rect width="30" height="20" fill="#A51931"/><rect y="3.33" width="30" height="13.34" fill="#F4F5F8"/><rect y="6.67" width="30" height="6.66" fill="#2D2A4A"/>',
    my: Array.from({ length: 14 }, (_, k) => `<rect y="${(k * 20 / 14).toFixed(2)}" width="30" height="${(20 / 14).toFixed(2)}" fill="${k % 2 ? '#fff' : '#CC0001'}"/>`).join('')
      + '<rect width="15" height="11.43" fill="#010066"/><circle cx="5.6" cy="5.7" r="3.6" fill="#FFCC00"/><circle cx="6.8" cy="5.7" r="3" fill="#010066"/>' + star(10.8, 5.7, 2.4, '#FFCC00'),
    vn: '<rect width="30" height="20" fill="#DA251D"/>' + star(15, 10.4, 6.2, '#FFFF00'),
    kh: '<rect width="30" height="20" fill="#032EA1"/><rect y="5" width="30" height="10" fill="#E00025"/>'
      + '<path d="M8.6 14 H21.4 V13 H20.4 V11.2 H19.6 V9.4 L18.9 8.1 L18.2 9.4 V10.4 H16.6 V8.2 L15 5.6 L13.4 8.2 V10.4 H11.8 V9.4 L11.1 8.1 L10.4 9.4 V11.2 H9.6 V13 H8.6Z" fill="#fff"/>',
    jp: '<rect width="30" height="20" fill="#fff"/><circle cx="15" cy="10" r="6" fill="#BC002D"/>',
    ph: '<rect width="30" height="10" fill="#0038A8"/><rect y="10" width="30" height="10" fill="#CE1126"/><path d="M0 0 L17.3 10 L0 20Z" fill="#fff"/>'
      + '<circle cx="5.8" cy="10" r="2.1" fill="#FCD116"/>' + [[1.9, 2.8], [1.9, 17.2], [14, 10]].map(([x, y]) => star(x, y, 1, '#FCD116')).join(''),
    in: '<rect width="30" height="6.67" fill="#FF9933"/><rect y="6.67" width="30" height="6.66" fill="#fff"/><rect y="13.33" width="30" height="6.67" fill="#138808"/>'
      + '<circle cx="15" cy="10" r="2.7" fill="none" stroke="#000080" stroke-width=".5"/>'
      + `<path d="${Array.from({ length: 12 }, (_, k) => { const a = k * Math.PI / 12; return `M${(15 - 2.6 * Math.cos(a)).toFixed(2)} ${(10 - 2.6 * Math.sin(a)).toFixed(2)} L${(15 + 2.6 * Math.cos(a)).toFixed(2)} ${(10 + 2.6 * Math.sin(a)).toFixed(2)}`; }).join(' ')}" stroke="#000080" stroke-width=".3"/>`,
  };
  const flagOf = (p) => {
    if (canShowFlagEmoji && p.flag) return `<span class="tm-flag" aria-hidden="true">${p.flag}</span>`;
    if (FLAG_ART[p.code]) return `<svg class="tm-flag drawn" viewBox="0 0 30 20" aria-hidden="true">${FLAG_ART[p.code]}</svg>`;
    return '';
  };
  const PIN_COLOURS = ['#D9584A', '#3A57C4', '#6E9E5A', '#D6A23A', '#9A7BD0', '#2E9C9A', '#E07AA0'];

  // the drawing: longitude 66–148 and latitude 42 to -6 squeezed into a 600 x 300 sheet
  const MAP_W = 600, MAP_H = 300;
  const proj = (lat, lon) => [(lon - 66) / 82 * MAP_W, (42 - lat) / 48 * MAP_H];
  // simplified coastlines (lon, lat), drawn by hand: mainland Asia with India, Indochina and the
  // Malay peninsula, then the islands
  const LAND = [
    [[66,42],[123,42],[121.5,38],[119,35],[121.8,31],[120,27],[117,23.5],[113,22],[110,21],[108.6,21.6],[106.6,20.2],[105.8,18.6],
     [107,16.5],[108.8,15],[109.3,12],[108.6,10.9],[106.8,10.3],[105,8.6],[104.8,9.6],[104.5,10.4],[104.3,10.5],[104.15,10.55],[103.9,10.48],[103.6,10.5],[103.5,10.62],[103.6,10.85],[103.3,11.0],[103.15,11.3],[103.0,11.4],[102.9,11.65],[102.6,12.0],[102.3,12.2],[101.6,12.6],[100.9,12.7],[100.3,13.5],
     [99.9,12.5],[99.2,10.2],[100.3,8.4],[101.3,6.9],[102.3,6.2],[103.4,4.5],[103.5,2.6],[104.2,1.4],[103.5,1.25],[101.3,2.8],[100.4,4.8],
     [100.1,6.5],[98.5,8],[98.3,10],[98.6,13],[97.7,16.5],[94.5,16],[94.2,19.5],[92.3,21.5],[90,21.8],[88.5,21.6],[87,21],[86.5,20],
     [85,19.3],[82.3,16.6],[80.3,15.5],[80.2,13],[79.8,10.3],[78.2,8.4],[77.5,8.1],[76.3,9.8],[75,12.5],[74,15.5],[73,19],[72.8,21],
     [70.3,21],[68.8,22.5],[66,25]],
    [[95.3,5.6],[97.5,5.2],[100.4,2.2],[104,-1],[106,-6],[104,-6.5],[102,-4],[100.3,-1],[98.7,1.7]],                                  // Sumatra
    [[109.6,1.9],[110.5,1.6],[113,3.2],[115.4,5],[116.8,6.9],[119.2,5.2],[118,4.3],[117.8,1],[116.5,-1.5],[116,-4],[114.6,-4],[111,-3],[110.2,-1.7],[109,0.5]], // Borneo
    [[120.6,18.5],[122.2,18.5],[122,16.3],[121.6,14.3],[124,12.6],[123.9,13.8],[121.8,14.2],[120.6,14.4],[119.8,16.3]],             // Luzon
    [[122.5,11.8],[124,11.3],[125,10.2],[123.5,10],[122.3,10.6]],                                                                     // Visayas
    [[122,8],[123.5,8.7],[125.4,9.8],[126.6,7.2],[125.4,5.7],[124,6.5],[122.2,7]],                                                    // Mindanao
    [[117.2,8.4],[119.5,10.6],[119.7,11.3],[117.3,8.8]],                                                                               // Palawan
    [[120.3,22.6],[121.5,25.2],[121.9,24.8],[120.7,22]],                                                                               // Taiwan
    [[108.7,19.2],[110,20.1],[111,19.6],[109.6,18.2]],                                                                                 // Hainan
    [[79.8,9.6],[80.2,9.8],[81.8,7.5],[81.2,6.2],[80,6],[79.8,8]],                                                                     // Sri Lanka
    [[126.1,35],[126.5,37.7],[125,40],[124.5,42],[130.5,42],[129.4,40],[128.4,38.3],[129.4,36],[129.2,35.2],[127,34.6]],              // Korea
    [[130.9,34],[132.5,35.4],[135.3,35.7],[136.8,37.3],[139.5,38.2],[140,40.8],[141.4,41.3],[141.5,40],[141,38.3],[140.9,36.9],[140.8,35.6],
     [139.8,35],[138.8,34.6],[137,34.6],[135.2,33.8],[133.2,34.3],[131,33.9]],                                                         // Honshu
    [[129.7,33.7],[131,33.9],[131.8,32],[130.6,31],[129.8,32.7]],                                                                      // Kyushu
    [[132.4,33.2],[134.3,34.2],[134.7,33.8],[133,32.8]],                                                                               // Shikoku
    [[139.9,41.5],[141.2,41.8],[143.2,42],[141.5,42],[140.3,42]],                                                                       // Hokkaido's tip
  ];
  const pathOf = (pts) => {
    // soften the corners: a curve through the midpoints of each edge
    const p = pts.map(([lon, lat]) => proj(lat, lon));
    const mid = p.map(([x, y], i) => { const [x2, y2] = p[(i + 1) % p.length]; return [(x + x2) / 2, (y + y2) / 2]; });
    let d = `M${mid[mid.length - 1][0].toFixed(1)} ${mid[mid.length - 1][1].toFixed(1)}`;
    p.forEach(([x, y], i) => { d += ` Q${x.toFixed(1)} ${y.toFixed(1)} ${mid[i][0].toFixed(1)} ${mid[i][1].toFixed(1)}`; });
    return d + 'Z';
  };

  /* ---------- Around Cambodia: the places at home, shown when the map zooms in on Cambodia ----------
     lat / lon put each pin on the map; area is a short note on where it is. */
  const KH_PLACES = [
    { name: 'Siem Reap', area: 'Northwest · Angkor', lat: 13.36, lon: 103.86 },
    { name: 'Kampot', area: 'South coast', lat: 10.61, lon: 104.18 },
    { name: 'Kep', area: 'South coast', lat: 10.45, lon: 104.36 },
    { name: 'Koh Rong', area: 'Island · Gulf of Thailand', lat: 10.72, lon: 103.24 },
    { name: 'Battambang', area: 'Northwest', lat: 13.1, lon: 103.2 },
    { name: 'Pursat', area: 'West · Tonle Sap', lat: 12.54, lon: 103.92 },
    { name: 'Kratie', area: 'Northeast · on the Mekong', lat: 12.49, lon: 106.02 },
    { name: 'Sihanoukville', area: 'South coast', lat: 10.63, lon: 103.52 },
    { name: 'Kampong Thom', area: 'Central', lat: 12.71, lon: 104.89 },
    { name: 'Prey Veng', area: 'Southeast', lat: 11.48, lon: 105.33 },
    { name: 'Svay Rieng', area: 'Southeast', lat: 11.09, lon: 105.8 },
    { name: 'Kandal', area: 'Around Phnom Penh', lat: 11.2, lon: 105.0 },
    { name: 'Takeo', area: 'South', lat: 10.99, lon: 104.79 },
    { name: 'Kampong Speu', area: 'Central west', lat: 11.45, lon: 104.52 },
    { name: 'Banteay Meanchey', area: 'Northwest', lat: 13.59, lon: 102.97 },
    { name: 'Mondulkiri', area: 'Northeast highlands', lat: 12.45, lon: 107.19 },
  ];
  // Cambodia drawn by hand (lon, lat): the border, the Tonle Sap lake, the Mekong and its rivers, Koh Rong
  const KH_BORDER = [[102.36,13.56],[102.75,13.95],[103.1,14.3],[103.6,14.42],[104.3,14.38],[105.0,14.33],[105.25,14.35],[105.6,14.15],[106.0,14.36],
    [106.5,14.55],[107.0,14.45],[107.55,14.6],[107.5,14.0],[107.6,13.4],[107.48,12.7],[107.6,12.3],[107.2,11.95],[106.8,11.65],[106.45,11.7],[106.25,11.25],
    [106.0,10.95],[105.85,11.15],[105.6,11.0],[105.2,10.9],[104.95,10.6],[104.5,10.42],[104.3,10.5],[104.15,10.55],[103.9,10.48],[103.6,10.5],
    [103.5,10.62],[103.6,10.85],[103.3,11.0],[103.15,11.3],[103.0,11.4],[102.92,11.65],[102.8,12.0],[102.7,12.5],[102.5,12.75],[102.6,13.2]];
  const KH_LAKE = [[103.66,13.12],[103.98,13.1],[104.3,12.78],[104.46,12.46],[104.26,12.5],[103.92,12.84],[103.66,13.02]];
  const KH_MEKONG = [[105.85,14.4],[105.88,13.95],[105.97,13.52],[106.05,13.0],[106.02,12.49],[105.75,12.2],[105.46,11.99],[105.15,11.78],[104.93,11.57],[105.05,11.2],[105.15,10.85],[105.3,10.5]];
  const KH_TONLE_SAP_RIVER = [[104.46,12.46],[104.68,12.1],[104.85,11.8],[104.93,11.57]];
  const KH_KOH_RONG = [[103.17,10.66],[103.22,10.8],[103.31,10.77],[103.27,10.66]];
  // the camera: the whole sheet, and the close-up on Cambodia (same 2:1 shape)
  const VIEW_ASIA = [0, 0, 600, 300], VIEW_KH = [249, 163.5, 72, 36];
  const KH_PIN = VIEW_KH[2] / 600 * 1.05;   // keeps the close-up pins the same size on screen

  function travelMap() {
    const [hx, hy] = proj(HOME.lat, HOME.lon);
    const pts = PLACES.map((p) => proj(p.lat, p.lon));
    const line = (arr) => 'M' + arr.map(([lon, lat]) => proj(lat, lon).map((v) => v.toFixed(2)).join(' ')).join(' L');
    // flight paths: an arc from home out to each place
    const arc = ([x, y]) => {
      const dx = x - hx, dy = y - hy, len = Math.hypot(dx, dy) || 1, bend = Math.min(60, len * .28);
      const cx = (hx + x) / 2 + dy / len * bend * (dx > 0 ? -1 : 1), cy = (hy + y) / 2 - Math.abs(dx / len) * bend;
      return { d: `M${hx.toFixed(1)} ${hy.toFixed(1)} Q${cx.toFixed(1)} ${cy.toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)}`, mid: [(hx + 2 * cx + x) / 4, (hy + 2 * cy + y) / 4], ang: Math.atan2(y - hy, x - hx) * 180 / Math.PI };
    };
    const arcs = pts.map(arc);
    let far = 0;
    pts.forEach(([x, y], i) => { if (Math.hypot(x - hx, y - hy) > Math.hypot(pts[far][0] - hx, pts[far][1] - hy)) far = i; });
    const pinShape = (c, n, key) => `<g class="tm-pin" data-place="${key}"><ellipse cx="0" cy="1" rx="5.4" ry="1.9" fill="#000" opacity=".18"/>
        <g class="tm-pin-in"><path d="M0 0 C-2.4 -4.6 -8.4 -7.8 -8.4 -14.6 A8.4 8.4 0 1 1 8.4 -14.6 C8.4 -7.8 2.4 -4.6 0 0Z" fill="${c}" stroke="#FFFDF7" stroke-width="1"/>
        <circle cx="0" cy="-14.6" r="5.4" fill="#FFFDF7"/><text x="0" y="-11.6" text-anchor="middle" class="tm-num" fill="${c}">${n}</text></g></g>`;
    const pin = ([x, y], i) => `<g transform="translate(${x.toFixed(1)} ${y.toFixed(1)})">${pinShape(PIN_COLOURS[i % PIN_COLOURS.length], i + 1, i)}</g>`;
    const khPin = (p, i) => {
      const [x, y] = proj(p.lat, p.lon);
      return `<g transform="translate(${x.toFixed(2)} ${y.toFixed(2)}) scale(${KH_PIN.toFixed(4)})">${pinShape(PIN_COLOURS[i % PIN_COLOURS.length], i + 1, 'k' + i)}</g>`;
    };
    const lw = HOME.label.length * 6.6 + 18;
    const homeMark = (labelBelow) => `
          <ellipse cx="0" cy="1" rx="7" ry="2.4" fill="#000" opacity=".18"/>
          <path d="M-7.6 -1 V-10.4 L0 -17 L7.6 -10.4 V-1Z" fill="#FFFDF7" stroke="#2A2F3A" stroke-width="1.3" stroke-linejoin="round"/>
          <path d="M-9.4 -9.6 L0 -18 L9.4 -9.6" fill="none" stroke="#D9584A" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
          <rect x="-2.2" y="-7" width="4.4" height="6" rx=".8" fill="#D6A23A"/>
          ${labelBelow ? `<rect x="-${(lw / 2).toFixed(1)}" y="5" width="${lw.toFixed(1)}" height="16" rx="8" fill="#2A2F3A"/><text x="0" y="16" text-anchor="middle" class="tm-home-label">${HOME.label}</text>` : ''}`;
    const t = (lon, lat, cls, txt) => { const [x, y] = proj(lat, lon); return `<text x="${x.toFixed(2)}" y="${y.toFixed(2)}" class="${cls}" text-anchor="middle">${txt}</text>`; };
    return `
      <svg class="tm-map" viewBox="${VIEW_ASIA.join(' ')}" role="img" aria-label="A hand-drawn map of Asia with home in ${HOME.label} and ${PLACES.length} pinned places: ${PLACES.map((p) => p.name).join(', ')}">
        <defs>
          <linearGradient id="tmSea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D6E8F1"/><stop offset="1" stop-color="#BCD5E4"/></linearGradient>
          <pattern id="tmWaves" width="44" height="24" patternUnits="userSpaceOnUse"><path d="M4 12 q4 -4 8 0 t8 0" stroke="#9FBDD3" stroke-width="1.1" fill="none" opacity=".6"/></pattern>
          <pattern id="tmWavesSm" width="5.2" height="2.8" patternUnits="userSpaceOnUse"><path d="M.5 1.4 q.5 -.5 1 0 t1 0" stroke="#9FBDD3" stroke-width=".13" fill="none" opacity=".7"/></pattern>
        </defs>
        <rect width="${MAP_W}" height="${MAP_H}" fill="url(#tmSea)"/>
        <rect class="tm-asia-only" width="${MAP_W}" height="${MAP_H}" fill="url(#tmWaves)"/>
        <rect class="tm-kh-only" x="${VIEW_KH[0]}" y="${VIEW_KH[1]}" width="${VIEW_KH[2]}" height="${VIEW_KH[3]}" fill="url(#tmWavesSm)"/>
        <g fill="#E3E8C9" stroke="#9FB384" stroke-width="1.2" stroke-linejoin="round">${LAND.map((l) => `<path d="${pathOf(l)}" vector-effect="non-scaling-stroke"/>`).join('')}</g>
        <!-- Cambodia: always picked out in a warmer tone; lake, rivers and names appear up close -->
        <path d="${pathOf(KH_BORDER)}" fill="#F1E4C3" stroke="#B6905A" stroke-width="1.1" vector-effect="non-scaling-stroke"/>
        <g class="tm-kh-only">
          <path d="${line(KH_MEKONG)}" fill="none" stroke="#9EC3DA" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
          <path d="${line(KH_TONLE_SAP_RIVER)}" fill="none" stroke="#9EC3DA" stroke-width="2" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
          <path d="${pathOf(KH_LAKE)}" fill="#BCD5E4" stroke="#9EC3DA" stroke-width="1" vector-effect="non-scaling-stroke"/>
          <path d="${pathOf(KH_KOH_RONG)}" fill="#F1E4C3" stroke="#B6905A" stroke-width="1" vector-effect="non-scaling-stroke"/>
          ${t(101.6, 13.6, 'tm-country-label', 'THAILAND')}${t(106.3, 14.95, 'tm-country-label', 'LAOS')}${t(107.4, 11.1, 'tm-country-label', 'VIETNAM')}
          ${t(102.45, 10.55, 'tm-sea-label', 'Gulf of Thailand')}${t(104.05, 12.92, 'tm-water-label', 'Tonle Sap')}${t(105.62, 13.3, 'tm-water-label', 'Mekong')}
          ${t(104.6, 13.95, 'tm-kh-label', 'CAMBODIA')}
        </g>
        <g class="tm-asia-only tm-deco">
          <g fill="#C9D3A6" opacity=".8"><circle cx="150" cy="120" r="7"/><circle cx="162" cy="128" r="5"/><circle cx="214" cy="96" r="6"/><circle cx="110" cy="60" r="6"/></g>
          <g fill="#D6CBA6" stroke="#B0A27A" stroke-width=".9"><path d="M140 52 l10 -17 l10 17Z M156 52 l8 -13 l8 13Z M178 48 l9 -15 l9 15Z"/></g>
          <g fill="#FFFFFF" opacity=".85"><path d="M146.4 41.6 l3.6 -6.6 l3.6 6.6 l-1.8 -1.2 l-1.8 1.3 l-1.8 -1.3Z M183.6 40.4 l3.4 -5.8 l3.4 5.8 l-1.7 -1.1 l-1.7 1.2 l-1.7 -1.2Z"/></g>
          <path d="M200 0 V300 M400 0 V300" stroke="#8C7A5A" stroke-width="1" opacity=".1"/>
          <path d="M0 150 H600" stroke="#FFFFFF" stroke-width="1.4" opacity=".28"/>
        </g>
        <g class="tm-asia-only">
          <g class="tm-routes" fill="none" stroke="#3A57C4" stroke-width="1.6" stroke-dasharray="2 6" stroke-linecap="round" opacity=".7">${arcs.map((a, i) => `<path class="tm-route" data-place="${i}" d="${a.d}"/>`).join('')}</g>
          <g class="tm-plane" transform="translate(${arcs[far].mid[0].toFixed(1)} ${arcs[far].mid[1].toFixed(1)}) rotate(${arcs[far].ang.toFixed(0)})">
            <path d="M-9 -4.5 L11 0 L-9 4.5 L-5.5 0Z" fill="#FFFDF7" stroke="#2A2F3A" stroke-width="1.1" stroke-linejoin="round"/><path d="M-5.5 0 L11 0 L-7 2.8Z" fill="#E4E9F8"/>
          </g>
          ${pts.map(pin).join('')}
          <g class="tm-home" data-zoom="kh" tabindex="0" role="button" aria-label="Home, ${HOME.label}: zoom in on Cambodia" transform="translate(${hx.toFixed(1)} ${hy.toFixed(1)})">
            <circle r="22" cy="-6" fill="transparent"/>${homeMark(true)}
            <circle class="tm-home-ring" r="13" cy="-9" fill="none" stroke="#D9584A" stroke-width="1.4"/>
          </g>
          <g transform="translate(562 262)">
            <circle r="20" fill="#FFFDF7" opacity=".85" stroke="#8C7A5A" stroke-width="1"/>
            <path d="M0 -15 L3.6 0 L0 15 L-3.6 0Z" fill="#2A2F3A"/><path d="M0 -15 L3.6 0 L-3.6 0Z" fill="#D9584A"/>
            <text x="0" y="-23" text-anchor="middle" class="tm-n">N</text>
          </g>
        </g>
        <g class="tm-kh-only">
          <g transform="translate(${hx.toFixed(2)} ${hy.toFixed(2)}) scale(${KH_PIN.toFixed(4)})">${homeMark(false)}</g>
          ${KH_PLACES.map(khPin).join('')}
        </g>
      </svg>`;
  }

  function placesPanel() {
    const card = (p, i, key, sub) => `
      <li class="tm-card" data-place="${key}" tabindex="0" style="--pin:${PIN_COLOURS[i % PIN_COLOURS.length]}">
        <span class="tm-badge">${i + 1}</span>
        ${p.year ? `<span class="tm-year mono">${p.year}</span>` : ''}
        <b>${p.flag !== undefined ? flagOf(p) : ''}${p.city ? `${p.city}, ` : ''}${p.name}</b>
        <span class="mono tm-country">${sub}</span>
        ${p.doing ? `<p>${p.doing}</p>` : ''}
      </li>`;
    const kh = { flag: '🇰🇭', code: 'kh' };
    return `<p class="lead">Travel is one of my favourite things. Most trips I take with my friends, and sometimes I go solo, for a slower trip of my own. I've explored a lot around Cambodia, and these are the places I've been abroad so far, flying out from home in ${HOME.label}.</p>
      <div class="tm" id="tm">
        <div class="tm-frame">
          ${travelMap()}
          <div class="tm-zoombar">
            <button class="tm-back" type="button" data-zoom="asia">← Back to Asia</button>
            <span class="tm-zoomtitle">${flagOf(kh)}Around Cambodia · ${KH_PLACES.length} places</span>
          </div>
        </div>
        <ol class="tm-cards tm-asia-cards">${PLACES.map((p, i) => card(p, i, i, p.region)).join('')}
          <li class="tm-card tm-home-card" data-zoom="kh" tabindex="0" role="button" style="--pin:#D9584A">
            <span class="tm-badge">⌂</span>
            <b>${flagOf(kh)}Around Cambodia</b>
            <span class="mono tm-country">${KH_PLACES.length} places · zoom in</span>
          </li>
        </ol>
        <ol class="tm-cards tm-kh-cards">${KH_PLACES.map((p, i) => card(p, i, 'k' + i, p.area)).join('')}</ol>
      </div>
      <p class="mono tm-hint">Point at a place to find it on the map · tap home to zoom into Cambodia</p>`;
  }

  // Zooming: the map's camera glides between all of Asia and Cambodia
  let tmAnim = 0;
  function zoomMap(toKh) {
    const tm = document.getElementById('tm'), svg = tm?.querySelector('.tm-map');
    if (!svg || tm.classList.contains('kh') === toKh) return;
    tm.classList.toggle('kh', toKh);
    if (!svg.dataset.asiaLabel) svg.dataset.asiaLabel = svg.getAttribute('aria-label');
    svg.setAttribute('aria-label', toKh ? `A close-up map of Cambodia with ${KH_PLACES.length} pinned places: ${KH_PLACES.map((p) => p.name).join(', ')}` : svg.dataset.asiaLabel);
    const from = svg.getAttribute('viewBox').split(' ').map(Number), to = toKh ? VIEW_KH : VIEW_ASIA;
    cancelAnimationFrame(tmAnim);
    if (reduceMotion) { svg.setAttribute('viewBox', to.join(' ')); return; }
    const t0 = performance.now() + 160, ms = 1000;   // a short pause first, while the markers fade out
    // zoom in a "log" way so the speed feels even at every scale
    const lerpBox = (k) => {
      const s0 = from[2], s1 = to[2], s = s0 * Math.pow(s1 / s0, k), f = (s0 - s) / (s0 - s1 || 1);
      return [from[0] + (to[0] - from[0]) * f, from[1] + (to[1] - from[1]) * f, s, s / 2];
    };
    const step = (now) => {
      const k = Math.max(0, Math.min(1, (now - t0) / ms)), e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
      svg.setAttribute('viewBox', lerpBox(e).map((v) => v.toFixed(3)).join(' '));
      if (k < 1) tmAnim = requestAnimationFrame(step);
    };
    tmAnim = requestAnimationFrame(step);
    (toKh ? tm.querySelector('.tm-back') : tm.querySelector('.tm-home'))?.focus({ preventScroll: true });
  }
  dialog?.addEventListener('click', (e) => {
    const z = e.target.closest('[data-zoom]');
    if (z && body.querySelector('.tm-map')) zoomMap(z.dataset.zoom === 'kh');
  });
  dialog?.addEventListener('keydown', (e) => {
    const z = e.target.closest('[data-zoom]');
    if (z && (e.key === 'Enter' || e.key === ' ') && z.tagName !== 'BUTTON') { e.preventDefault(); zoomMap(z.dataset.zoom === 'kh'); }
  });

  // pointing at a card lights up its pin and flight path, and the other way round
  const lightPlace = (i) => body.querySelectorAll('[data-place]').forEach((n) => n.classList.toggle('hot', n.dataset.place === i));
  dialog?.addEventListener('pointerover', (e) => {
    const hit = e.target.closest('[data-place]');
    if (hit && body.querySelector('.tm-map')) lightPlace(hit.dataset.place);
  });
  dialog?.addEventListener('focusin', (e) => {
    const hit = e.target.closest('.tm-card');
    if (hit) lightPlace(hit.dataset.place);
  });

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
    map: { label: "Where I've been", open: () => panel('Pinned to the wall', "Where I've <em>been</em>", placesPanel()) },
    phone: { label: 'Say hello', open: () => panel('Ring ring', 'Say <em>hello</em>',
      `<p class="lead">I'm always happy to talk about new projects, ideas, or just say hi.</p>
      <div class="panel-actions"><a class="pill" href="mailto:${EMAIL}" data-copy="${EMAIL}">${EMAIL} <span aria-hidden="true">↗</span></a>
      ${Object.entries(SOCIALS).map(([label, url]) => `<a class="ghost" href="${url}" target="_blank" rel="noopener">${label}</a>`).join('')}</div>
      <p class="mono copy-hint" style="margin-top:14px">click the email to copy it</p>`) },
    record: { label: 'On repeat',
      // first click drops the needle (the record spins, notes float up); next click opens the playlist
      act: () => {
        const r = el('record');
        if (!r.classList.contains('playing')) { setRecord(true); say('Now playing ♪ click again for the playlist'); }
        else {
          if (document.getElementById('deck')) reopenPanel();  // still there from last time: keep the player as it is
          else openPanel(THINGS.record.open());
          startDeck();
        }
      },
      open: () => panel('On the record player', 'On <em>repeat</em>', deckHTML()) },
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

  /* ---------- Sound switch (home page) ---------- */
  const soundBtn = document.getElementById('sound');
  if (soundBtn) {
    if (!window.RoomSound) soundBtn.hidden = true;  // very old browsers: no Web Audio
    else {
      const paint = () => {
        const on = window.RoomSound.enabled;
        soundBtn.classList.toggle('on', on);
        soundBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
        soundBtn.querySelector('.sound-label').textContent = on ? 'Sound on' : 'Sound off';
      };
      soundBtn.addEventListener('click', () => {
        const on = window.RoomSound.toggle();
        say(on ? (recordPlaying() ? 'Sound on ♪' : 'Sound on ♪ drop the needle on the record for music') : 'Sound off');
      });
      window.RoomSound.onChange(paint);
      paint();
    }
  }

  const yr = document.getElementById('yr');
  if (yr) yr.textContent = new Date().getFullYear();
})();
