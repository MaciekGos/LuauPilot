// LuauPilot - runs in the PAGE's own world. Keeps the chat site working when its tab is in the background, so
// streaming and rendering do not pause when you switch to Roblox Studio:
//   1. the site is told its tab is always visible (no "hidden" pauses in its own code);
//   2. requestAnimationFrame - which the browser stops completely in a background tab, and which many chat sites use
//      to draw the streamed text - falls back to a timer while the tab is really hidden.
(() => {
  try {
    // remember the REAL state before it is hidden from the page
    const realGetter = (() => { try { return Object.getOwnPropertyDescriptor(Document.prototype, "hidden").get; } catch { return null; } })();
    const reallyHidden = () => { try { return realGetter ? !!realGetter.call(document) : false; } catch { return false; } };

    // registered BEFORE the listeners below that hide visibilitychange from the page (they stop all later listeners)
    let flush = () => {};
    window.addEventListener("visibilitychange", () => { setTimeout(() => flush(), 0); }, true);   // window capture runs first of all

    const def = (proto, key, val) => { try { Object.defineProperty(proto, key, { configurable: true, get: () => val }); } catch { /* ignore */ } };
    def(Document.prototype, "hidden", false);
    def(Document.prototype, "webkitHidden", false);
    def(Document.prototype, "visibilityState", "visible");
    def(Document.prototype, "webkitVisibilityState", "visible");
    const stop = (e) => e.stopImmediatePropagation();
    document.addEventListener("visibilitychange", stop, true);
    window.addEventListener("visibilitychange", stop, true);
    window.addEventListener("pagehide", stop, true);
    try { Document.prototype.hasFocus = () => true; } catch { /* ignore */ }

    // requestAnimationFrame that keeps running in a background tab
    const nativeRaf = window.requestAnimationFrame.bind(window);
    const nativeCaf = window.cancelAnimationFrame.bind(window);
    const pending = new Map();     // native handle -> callback, for frames asked for while the tab was visible
    const timers = new Map();      // our handle -> timer id, for frames asked for while hidden
    let seq = 2000000000;
    const runLater = (cb) => { try { cb(performance.now()); } catch (e) { setTimeout(() => { throw e; }); } };

    window.requestAnimationFrame = (cb) => {
      if (typeof cb !== "function") return nativeRaf(cb);
      if (reallyHidden()) {
        const id = ++seq;
        timers.set(id, setTimeout(() => { timers.delete(id); runLater(cb); }, 16));
        return id;
      }
      const id = nativeRaf((t) => { pending.delete(id); cb(t); });
      pending.set(id, cb);
      return id;
    };
    window.cancelAnimationFrame = (id) => {
      if (timers.has(id)) { clearTimeout(timers.get(id)); timers.delete(id); return; }
      pending.delete(id);
      nativeCaf(id);
    };
    // frames that were waiting when the tab went to the background would wait for ever: run them from a timer
    flush = () => {
      if (!reallyHidden()) return;
      for (const [id, cb] of Array.from(pending)) { nativeCaf(id); pending.delete(id); setTimeout(() => runLater(cb), 16); }
    };
    window.__lpRafFlush = () => flush();
  } catch { /* never break the page */ }
})();
