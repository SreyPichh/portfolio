/* =========================================================
   Sound for the home office, made live with the Web Audio API
   (no audio files, nothing to license):
   - six soft lo-fi tunes for the record player, one per track,
     with Rhodes-style chords, bass, a lazy beat, a little melody
     and vinyl crackle
   - ambience outside the window: birdsong by day, crickets at night
   Browsers only allow sound after a click or key press, so nothing
   plays until the visitor turns sound on or drops the needle.
   script.js talks to this through window.RoomSound.
   ========================================================= */
(function () {
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) { window.RoomSound = null; return; }

  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const mtof = (m) => 440 * Math.pow(2, (m - 69) / 12);
  const rng = (seed) => () => {  // small seeded random, so each tune always plays the same way
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  /* ---------- The six tunes: key (MIDI root), tempo, and a four-bar chord loop ---------- */
  const Q = { maj7: [0, 4, 7, 11], maj9: [0, 4, 7, 11, 14], m7: [0, 3, 7, 10], m9: [0, 3, 7, 10, 14], dom9: [0, 4, 10, 14], m11: [0, 3, 10, 14, 17] };
  const SONGS = [
    { root: 53, bpm: 70, seed: 11, prog: [[2, 'm9'], [7, 'dom9'], [0, 'maj9'], [9, 'm7']] },   // F: ii V I vi
    { root: 50, bpm: 74, seed: 23, prog: [[0, 'maj7'], [9, 'm9'], [5, 'maj9'], [4, 'm7']] },   // D
    { root: 48, bpm: 66, seed: 37, prog: [[9, 'm9'], [5, 'maj7'], [0, 'maj9'], [7, 'dom9']] }, // C
    { root: 51, bpm: 64, seed: 41, prog: [[0, 'maj9'], [5, 'maj7'], [3, 'm11'], [7, 'm7']] },  // Eb, slow and dreamy
    { root: 45, bpm: 76, seed: 59, prog: [[0, 'm9'], [5, 'm9'], [10, 'maj7'], [3, 'maj9']] },  // A minor
    { root: 55, bpm: 70, seed: 67, prog: [[5, 'maj9'], [4, 'm7'], [2, 'm9'], [0, 'maj7']] },   // G
  ];
  const PENTA = [0, 2, 4, 7, 9];

  let ctx = null, master, music, amb, lofi, noise, crackle, crackleGain, flutter, meter;
  let enabled = false, wantsMusic = false, song = SONGS[0], songIndex = 0;
  let step = 0, nextTime = 0, timer = null, rand = rng(1);
  let daytime = 0.35, birdTimer = null, cricketTimer = null;
  const listeners = new Set();
  const emit = () => listeners.forEach((fn) => fn());

  try { enabled = localStorage.getItem('sound') === 'on'; } catch (e) {}

  // the "sound" of a small warm room: a few seconds of fading, softened noise
  function roomImpulse(seconds) {
    const rate = ctx.sampleRate, len = Math.floor(rate * seconds);
    const buf = ctx.createBuffer(2, len, rate);
    for (let ch = 0; ch < 2; ch++) {
      const d = buf.getChannelData(ch);
      let smooth = 0;
      for (let i = 0; i < len; i++) {
        smooth += ((Math.random() * 2 - 1) - smooth) * .35;   // take the hiss off the tail
        d[i] = smooth * Math.pow(1 - i / len, 3.2) * (i < rate * .012 ? i / (rate * .012) : 1);
      }
    }
    return buf;
  }

  function setup() {
    if (ctx) return;
    ctx = new AC();
    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -4; comp.ratio.value = 12; comp.knee.value = 4; comp.attack.value = .003; comp.release.value = .25;  // only a safety net: a squashing compressor (with its automatic make-up gain) made the beat pump
    master = ctx.createGain(); master.gain.value = 0;
    master.connect(comp).connect(ctx.destination);
    meter = ctx.createAnalyser(); meter.fftSize = 1024;
    comp.connect(meter);

    // music: everything goes through a warm low-pass, which is most of the lo-fi feel
    lofi = ctx.createBiquadFilter(); lofi.type = 'lowpass'; lofi.frequency.value = 1500; lofi.Q.value = .3;
    music = ctx.createGain(); music.gain.value = 0;
    music.connect(lofi).connect(master);
    // a soft room reverb under the music, so it blends instead of sounding dry and close
    const verb = ctx.createConvolver();
    verb.buffer = roomImpulse(2.6);
    const wet = ctx.createGain(); wet.gain.value = .32;
    lofi.connect(verb).connect(wet).connect(master);
    amb = ctx.createGain(); amb.gain.value = .9;
    amb.connect(master);

    // a slow wobble in pitch, like a slightly warped record
    flutter = ctx.createOscillator(); flutter.frequency.value = .45;
    const depth = ctx.createGain(); depth.gain.value = 6;  // cents
    flutter.connect(depth); flutter.start();
    flutter.depth = depth;

    // white noise for drums and hiss
    noise = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
    const d = noise.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;

    // vinyl crackle: soft hiss with random little pops, looped
    const len = ctx.sampleRate * 4;
    crackle = ctx.createBuffer(1, len, ctx.sampleRate);
    const c = crackle.getChannelData(0);
    for (let i = 0; i < len; i++) c[i] = (Math.random() * 2 - 1) * .012;
    for (let k = 0; k < 45; k++) {
      const at = Math.floor(Math.random() * (len - 200)), amp = (Math.random() ** 3) * .25 + .03;
      for (let j = 0; j < 60; j++) c[at + j] += (Math.random() * 2 - 1) * amp * Math.exp(-j / 6);
    }
    crackleGain = ctx.createGain(); crackleGain.gain.value = 0;
    const hp = ctx.createBiquadFilter(); hp.type = 'bandpass'; hp.frequency.value = 2200; hp.Q.value = .5;
    crackleGain.connect(hp).connect(master);
    const src = ctx.createBufferSource(); src.buffer = crackle; src.loop = true; src.connect(crackleGain); src.start();
  }

  /* ---------- Instruments ---------- */
  function wobble(o) {  // share the record's slow pitch wobble, and let go of it when the note ends
    flutter.depth.connect(o.detune);
    o.onended = () => { try { flutter.depth.disconnect(o.detune); } catch (e) {} };
  }

  function env(g, t, peak, attack, decay, sustain, release, end) {
    // start silent right away: a gain node is at full volume until told otherwise, and the
    // oscillator may start a moment before the envelope does (the notes of a chord roll in)
    g.gain.value = 0.0001;
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(peak, t + attack);
    g.gain.exponentialRampToValueAtTime(Math.max(peak * sustain, 0.0001), t + attack + decay);
    g.gain.setValueAtTime(Math.max(peak * sustain, 0.0001), end);
    g.gain.exponentialRampToValueAtTime(0.0001, end + release);
  }

  function keys(notes, t, dur, vel = 1) {  // electric-piano chord
    notes.forEach((m, n) => {
      const f = mtof(m);
      const g = ctx.createGain(); g.connect(music);
      env(g, t + n * .026, .04 * vel, .05, 1.8, .42, .9, t + dur);
      [['sine', 1, 1], ['sine', 2, .06]].forEach(([type, mul, lvl]) => {
        const o = ctx.createOscillator(); o.type = type; o.frequency.value = f * mul;
        o.detune.value = (Math.random() - .5) * 5;
        wobble(o);
        const og = ctx.createGain(); og.gain.value = lvl;
        o.connect(og).connect(g); o.start(t); o.stop(t + dur + .6);
      });
    });
  }

  function bass(m, t, dur) {
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = mtof(m);
    const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 380;
    const g = ctx.createGain();
    env(g, t + .02, .14, .07, .4, .6, .25, t + dur);
    o.connect(f).connect(g).connect(music); o.start(t); o.stop(t + dur + .2);
  }

  function lead(m, t, dur) {
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = mtof(m);
    wobble(o);
    const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 1400;
    const g = ctx.createGain();
    env(g, t, .04, .09, .6, .45, .5, t + dur);
    o.connect(f).connect(g).connect(music); o.start(t); o.stop(t + dur + .4);
  }

  function kick(t) {
    const o = ctx.createOscillator(); o.type = 'sine';
    o.frequency.setValueAtTime(82, t); o.frequency.exponentialRampToValueAtTime(40, t + .16);
    const g = ctx.createGain();
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(.13, t + .012); g.gain.exponentialRampToValueAtTime(.001, t + .36);
    o.connect(g).connect(music); o.start(t); o.stop(t + .35);
  }

  function hiss(t, type, freq, q, peak, decay) {  // snare and hats are filtered noise
    const s = ctx.createBufferSource(); s.buffer = noise;
    const f = ctx.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q;
    const g = ctx.createGain();
    g.gain.setValueAtTime(peak, t); g.gain.exponentialRampToValueAtTime(.0008, t + decay);
    s.connect(f).connect(g).connect(music); s.start(t, Math.random()); s.stop(t + decay + .02);
  }

  /* ---------- The beat: eighth-note steps, swung, scheduled a little ahead ---------- */
  function playStep(s, t) {
    const beat = 60 / song.bpm, bar = Math.floor(s / 8) % song.prog.length, pos = s % 8;
    const [deg, quality] = song.prog[bar];
    const root = song.root + deg;
    if (pos === 0) {
      keys(Q[quality].map((iv) => root + iv + (root + iv > 72 ? -12 : 0)), t, beat * 2.6);
      bass(root - 12 - (root - 12 > 47 ? 12 : 0), t, beat * 1.4);
    }
    if (pos === 5 && rand() < .55) keys(Q[quality].slice(1).map((iv) => root + iv + (root + iv > 72 ? -12 : 0)), t, beat * .9, .7);
    if (pos === 4) bass(root - 12 - (root - 12 > 47 ? 12 : 0) + (rand() < .3 ? 7 : 0), t, beat * .9);
    if (pos === 0 || (pos === 5 && rand() < .6)) kick(t);
    if (pos === 2 || pos === 6) hiss(t + .015, 'bandpass', 1300, .5, .055, .32);        // a soft brushed snare, laid back
    if (pos % 2 === 0) hiss(t, 'bandpass', 5200, .7, .012, .07);                       // a faint shaker on the beat
    // a sparse little melody from the pentatonic scale, different every bar but the same every play
    if (pos % 2 === 0 && rand() < .32) {
      const m = song.root + 24 + PENTA[Math.floor(rand() * PENTA.length)] + (rand() < .25 ? 12 : 0);
      lead(m, t, beat * (rand() < .5 ? .9 : 1.8));
    }
  }

  function scheduler() {
    const eighth = 60 / song.bpm / 2;
    while (nextTime < ctx.currentTime + .25) {
      const swing = step % 2 ? eighth * .18 : 0;
      playStep(step, nextTime + swing);
      nextTime += eighth;
      step++;
      if (step % (8 * song.prog.length) === 0) rand = rng(song.seed + step);  // each loop varies a touch
    }
  }

  function startMusic() {
    if (!ctx || timer) return;
    step = 0; rand = rng(song.seed);
    nextTime = ctx.currentTime + .08;
    music.gain.cancelScheduledValues(ctx.currentTime);
    crackleGain.gain.cancelScheduledValues(ctx.currentTime);
    music.gain.setTargetAtTime(1, ctx.currentTime, .25);
    crackleGain.gain.setTargetAtTime(.16, ctx.currentTime, .3);
    timer = setInterval(scheduler, 25);
    scheduler();
  }

  function stopMusic() {
    if (!ctx) return;
    clearInterval(timer); timer = null;
    music.gain.setTargetAtTime(0, ctx.currentTime, .12);
    crackleGain.gain.setTargetAtTime(0, ctx.currentTime, .2);
  }

  /* ---------- Outside: birds by day, crickets at night ---------- */
  const dayLevel = () => clamp(1 - (daytime - .72) / .14) * (daytime < .25 ? 1.2 : 1);
  const nightLevel = () => clamp((daytime - .8) / .12);

  function chirp(t, f0, f1, dur, vol, pan) {
    const o = ctx.createOscillator(); o.type = 'sine';
    o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + dur);
    const g = ctx.createGain();
    g.gain.setValueAtTime(.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + dur * .25); g.gain.exponentialRampToValueAtTime(.0001, t + dur);
    const p = ctx.createStereoPanner ? ctx.createStereoPanner() : null;
    if (p) { p.pan.value = pan; o.connect(g).connect(p).connect(amb); } else o.connect(g).connect(amb);
    o.start(t); o.stop(t + dur + .02);
  }

  function birdSong() {
    const lvl = dayLevel();
    if (enabled && ctx && lvl > .05) {
      const t = ctx.currentTime + .05, pan = Math.random() * 1.2 - .6, base = 2600 + Math.random() * 1800;
      const kind = Math.floor(Math.random() * 3), notes = 2 + Math.floor(Math.random() * 5);
      for (let i = 0; i < notes; i++) {
        const at = t + i * (kind === 2 ? .09 : .14) + Math.random() * .03;
        if (kind === 0) chirp(at, base * 1.25, base * .8, .08, .13 * lvl, pan);        // falling tweets
        else if (kind === 1) chirp(at, base * .85, base * 1.3, .1, .11 * lvl, pan);     // rising whistles
        else chirp(at, base * 1.4, base * 1.1, .05, .09 * lvl, pan);                   // quick trill
      }
    }
    birdTimer = setTimeout(birdSong, 1800 + Math.random() * 4200);
  }

  function crickets() {
    const lvl = nightLevel();
    if (enabled && ctx && lvl > .05) {
      [[4400, -.4, 0], [4750, .45, .42]].forEach(([f, pan, off]) => {
        if (Math.random() < .2) return;  // they don't always answer
        for (let i = 0; i < 3; i++) chirp(ctx.currentTime + .05 + off + i * .045, f, f * .98, .03, .07 * lvl, pan);
      });
    }
    cricketTimer = setTimeout(crickets, 850 + Math.random() * 500);
  }

  /* ---------- Turning things on and off ---------- */
  function wake() {
    setup();
    if (ctx.state === 'suspended') ctx.resume();
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setTargetAtTime(enabled ? .95 : 0, ctx.currentTime, .2);
    if (enabled && wantsMusic) startMusic(); else stopMusic();
    if (!birdTimer) birdSong();
    if (!cricketTimer) crickets();
  }

  function save() { try { localStorage.setItem('sound', enabled ? 'on' : 'off'); } catch (e) {} }

  // if sound was left on last visit, start as soon as the visitor touches the page
  if (enabled) {
    const first = () => { wake(); removeEventListener('pointerdown', first); removeEventListener('keydown', first); };
    addEventListener('pointerdown', first); addEventListener('keydown', first);
  }

  window.RoomSound = {
    get enabled() { return enabled; },
    get playing() { return wantsMusic; },
    setEnabled(on) { enabled = !!on; save(); wake(); emit(); },
    toggle() { this.setEnabled(!enabled); return enabled; },
    playMusic(i) {
      if (typeof i === 'number' && SONGS[i % SONGS.length] !== song) {
        stopMusic(); songIndex = i % SONGS.length; song = SONGS[songIndex];
      }
      wantsMusic = true;
      if (!enabled) { enabled = true; save(); }
      wake(); emit();
    },
    pauseMusic() { wantsMusic = false; stopMusic(); emit(); },
    setDaytime(t) { daytime = t; },
    // how loud it is right now, 0 to 1 (handy for anything that wants to move with the music)
    level() {
      if (!meter) return 0;
      const a = new Float32Array(meter.fftSize); meter.getFloatTimeDomainData(a);
      return Math.sqrt(a.reduce((sum, v) => sum + v * v, 0) / a.length);
    },
    get state() { return ctx ? ctx.state : 'not started'; },
    onChange(fn) { listeners.add(fn); },
  };
})();
