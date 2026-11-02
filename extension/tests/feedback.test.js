// The one-time feedback card: shows only when asked AND idle, answers go to the background worker, "later" hides it.
const fs = require("fs"), path = require("path");
const { load, check, done, ROOT } = require("./harness");
const w = load('<body><div id="app"><textarea placeholder="Message"></textarea></div></body>', [], "https://chat.deepseek.com/");
const sent = [];
let fbListener = null;
w.chrome = { runtime: { id: "x", getURL: (p) => p, getManifest: () => ({ version: "2" }), lastError: null,
  onMessage: { addListener(f) { const old = fbListener; fbListener = (m) => { f(m); old && old(m); }; } },
  sendMessage(m, cb) { sent.push(m); setTimeout(() => cb(m.t === "status" ? { t: "state", connected: false } : m.t === "feedback_get" ? { open: false } : {}), 5); } },
  storage: { onChanged: { addListener() {} }, local: { get(k, cb) { cb({}); }, set(o, cb) { cb && cb(); } } } };
const man = JSON.parse(fs.readFileSync(path.join(ROOT, "manifest.json"), "utf8"));
for (const f of man.content_scripts[1].js) w.eval(fs.readFileSync(path.join(ROOT, f), "utf8"));
const $ = (s) => w.document.querySelector(s);
setTimeout(() => {
  check("no card before the question is due", !$(".lp-fb"));
  w.LP.ui.status("running", "x");
  w.LP.ui.feedbackState({ open: true, url: "https://github.com/MaciekGos/LuaPilot/issues" });
  setTimeout(() => {
    check("not shown while LuauPilot is working", !$(".lp-fb"));
    w.LP.ui.status("idle");
    setTimeout(() => {
      check("shown when idle", !!$(".lp-fb") && /problems|blocked/.test($(".lp-fb").textContent));
      const btn = [...w.document.querySelectorAll(".lp-fb button")].find((b) => /problem/.test(b.textContent));
      btn.click();
      setTimeout(() => {
        check("answer sent to the worker", sent.some((m) => m.t === "feedback_answer" && m.action === "problem"));
        const a = $(".lp-fb a");
        check("sorry + GitHub Issues link", !!a && a.href.endsWith("/issues") && /sorry/i.test($(".lp-fb").textContent) && /very important/.test($(".lp-fb").textContent));
        done(); process.exit(0);
      }, 800);
    }, 900);
  }, 900);
}, 600);
