// LuauPilot - keeps the chat tab awake while a session runs, so switching to Roblox Studio does not slow the page
// down, freeze it or put it to sleep (Chrome "Memory Saver", Edge "Sleeping tabs"):
//   - an inaudible tone: a tab that plays audio is not throttled, frozen or discarded;
//   - a Web Lock held for as long as the session runs (a page holding a lock is not frozen);
//   - the background worker marks the tab as "do not discard".
// Only while a session is active and the "Keep this tab awake" setting is on.
(() => {
  const LP = (window.LP = window.LP || {});
  let ctx = null, osc = null, release = null, on = false, lastErr = "";

  const note = (type) => { try { if (LP.link && LP.link.alive && LP.link.alive()) chrome.runtime.sendMessage({ t: "awake", on: type }, () => void chrome.runtime.lastError); } catch { /* ignore */ } };

  function start() {
    if (on) return;
    on = true;
    try {
      if (navigator.locks && !release) {
        navigator.locks.request("luaupilot-awake", { mode: "shared" }, () => new Promise((res) => { release = res; })).catch(() => {});
      }
    } catch (e) { lastErr = String(e); }
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) {
        ctx = new AC();
        osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine"; osc.frequency.value = 25;        // far below what speakers play
        gain.gain.value = 0.002;                              // about -54 dB: counts as sound, cannot be heard
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start();
      }
    } catch (e) { lastErr = String(e); }
    note(true);
  }

  function stop() {
    if (!on) return;
    on = false;
    try { if (release) { release(); release = null; } } catch { /* ignore */ }
    try { if (osc) osc.stop(); } catch { /* ignore */ }
    try { if (ctx) ctx.close(); } catch { /* ignore */ }
    ctx = osc = null;
    note(false);
  }

  function poll() {
    let want = false;
    try { want = LP.settings && LP.settings.awake !== false && LP.agent && LP.agent.isActive && LP.agent.isActive(); } catch { want = false; }
    if (want && !on) start();
    else if (!want && on) stop();
    else if (on && ctx && ctx.state === "suspended") { try { ctx.resume(); } catch { /* ignore */ } }   // the browser may suspend it until you click
  }

  // a click anywhere lets a suspended audio context start
  const wake = () => { if (ctx && ctx.state === "suspended") { try { ctx.resume(); } catch { /* ignore */ } } };
  document.addEventListener("pointerdown", wake, true);
  document.addEventListener("keydown", wake, true);
  window.addEventListener("pagehide", stop);

  LP.awake = { poll, start, stop, status: () => ({ on, audio: ctx ? ctx.state : "none", lock: !!release, err: lastErr }) };
  setInterval(poll, 2000);
  try { chrome.runtime.onMessage.addListener((m) => { if (m && m.t === "pulse") poll(); }); } catch { /* ignore */ }
})();
