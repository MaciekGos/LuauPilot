# SPDX-License-Identifier: MIT
"""Short screen recordings of Roblox Studio, returned to the AI as a GIF.

    record_start  - starts recording the Studio window in the background (a few frames per second)
    record_stop   - stops it and returns the GIF (also saved in a temp folder)

The AI can do:  record_start -> any other command (play, move, click, build...) -> record_stop.
The recording runs in a thread inside the bridge, so the commands in between work as usual.
It stops by itself after max_seconds; record_stop then still returns what was recorded.

Frames are grabbed from the screen area of the Studio window (Windows). Keep Studio visible while recording.
"""
import base64
import ctypes
import io
import os
import sys
import tempfile
import threading
import time

IS_WIN = sys.platform == "win32"
OUT_DIR = os.environ.get("LP_REC_DIR") or os.path.join(tempfile.gettempdir(), "LuaPilot", "Recordings")
MAX_SECONDS = 30
DEFAULT_SECONDS = 20
MAX_FPS = 8
DEFAULT_FPS = 5
MAX_WIDTH = 800
DEFAULT_WIDTH = 640
TARGET_BYTES = 1_500_000        # the GIF is shrunk until it is under this (the chat upload has a size limit)
KEEP_RESULT_S = 600             # a recording that ended on its own waits this long for record_stop
KEEP_FILES_S = 24 * 3600

TOOLS = [
    {"name": "record_start",
     "description": "Start recording the Roblox Studio window (a short GIF, a few frames per second). Then send any other "
                    "command (start the game, move, click, build...) and finish with record_stop, which returns the GIF. "
                    "Stops by itself after max_seconds. Keep Studio visible while recording.",
     "inputSchema": {"type": "object", "properties": {
         "max_seconds": {"type": "integer", "description": "safety limit in seconds (default 20, max 30)"},
         "fps": {"type": "integer", "description": "frames per second (default 5, max 8)"},
         "width": {"type": "integer", "description": "GIF width in pixels (default 640, max 800)"},
         "region": {"type": "string", "enum": ["studio", "screen"], "description": "studio (default) = the Studio window, screen = the whole main screen"}}}},
    {"name": "record_stop",
     "description": "Stop the recording started with record_start and return it as a GIF (an animated picture of what "
                    "happened in Studio). Use it right after the command you wanted to watch.",
     "inputSchema": {"type": "object", "properties": {}}},
]
NAMES = {t["name"] for t in TOOLS}

_lock = threading.Lock()
_cur = None        # the running recording
_done = None       # a finished recording waiting for record_stop


# ── grabbing frames ───────────────────────────────────────────────────────
def _studio_rect():
    """(left, top, right, bottom) of the biggest visible Roblox Studio window, or raises."""
    if not IS_WIN:
        raise RuntimeError("Recording works on Windows only.")
    user32 = ctypes.windll.user32
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def visit(hwnd, _lp):
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        if n <= 0:
            return True
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, buf, n + 1)
        if "roblox studio" not in buf.value.lower():
            return True
        rect = ctypes.wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        w, h = rect.right - rect.left, rect.bottom - rect.top
        if w > 200 and h > 200 and not user32.IsIconic(hwnd):
            found.append((w * h, (rect.left, rect.top, rect.right, rect.bottom)))
        return True

    import ctypes.wintypes  # noqa: F401  (RECT)
    user32.EnumWindows(visit, 0)
    if not found:
        raise RuntimeError("Roblox Studio window not found (is it open and not minimized?).")
    return max(found)[1]


def _grab(region):
    from PIL import ImageGrab
    if region == "screen":
        return ImageGrab.grab(all_screens=False)
    left, top, right, bottom = _studio_rect()
    return ImageGrab.grab(bbox=(max(0, left), max(0, top), right, bottom), all_screens=True)


GRAB = _grab    # replaceable (tests)


class _Rec:
    def __init__(self, fps, seconds, width, region):
        self.fps, self.seconds, self.width, self.region = fps, seconds, width, region
        self.frames = []
        self.stop = threading.Event()
        self.error = ""
        self.started = time.time()
        self.thread = threading.Thread(target=self._run, daemon=True, name="lp-record")

    def _run(self):
        gap = 1.0 / self.fps
        nxt = time.time()
        try:
            while not self.stop.is_set() and time.time() - self.started < self.seconds:
                shot = GRAB(self.region)
                h = max(2, int(shot.height * self.width / shot.width))
                small = shot.convert("RGB").resize((self.width, h))
                self.frames.append(small.convert("P", palette=1, colors=128))     # palette frames keep memory small
                nxt += gap
                self.stop.wait(max(0.0, nxt - time.time()))
        except Exception as exc:  # noqa: BLE001 - reported by record_stop
            self.error = str(exc) or exc.__class__.__name__


def _clamp(value, lo, hi, default):
    try:
        return max(lo, min(hi, int(value)))
    except (TypeError, ValueError):
        return default


def _cleanup_old():
    try:
        for f in os.listdir(OUT_DIR):
            p = os.path.join(OUT_DIR, f)
            if time.time() - os.path.getmtime(p) > KEEP_FILES_S:
                os.remove(p)
    except OSError:
        pass


# ── building the GIF ──────────────────────────────────────────────────────
def _encode(frames, fps):
    """Frames -> GIF bytes under TARGET_BYTES (drops every other frame and shrinks if needed)."""
    from PIL import Image
    work = list(frames)
    scale = 1.0
    for _ in range(6):
        imgs = work if scale == 1.0 else [f.convert("RGB").resize((max(2, int(f.width * scale)), max(2, int(f.height * scale)))).convert("P", palette=1, colors=96) for f in work]
        buf = io.BytesIO()
        imgs[0].save(buf, format="GIF", save_all=True, append_images=imgs[1:], duration=int(1000 / fps) * (len(frames) // max(1, len(work)) or 1),
                     loop=0, optimize=True, disposal=1)
        data = buf.getvalue()
        if len(data) <= TARGET_BYTES or len(work) <= 4:
            return data, len(work), imgs[0].size
        if len(work) > 12:
            work = work[::2]
        else:
            scale *= 0.8
    return data, len(work), imgs[0].size


def _finish(rec):
    """-> tool result dict for a stopped recording."""
    rec.stop.set()
    rec.thread.join(timeout=5)
    if not rec.frames:
        raise RuntimeError("Nothing was recorded" + (f": {rec.error}" if rec.error else "."))
    secs = max(0.1, time.time() - rec.started)
    data, kept, size = _encode(rec.frames, rec.fps)
    os.makedirs(OUT_DIR, exist_ok=True)
    _cleanup_old()
    path = os.path.join(OUT_DIR, time.strftime("rec-%Y%m%d-%H%M%S.gif"))
    try:
        with open(path, "wb") as fh:
            fh.write(data)
    except OSError:
        path = "(not saved)"
    note = f" Recording stopped early: {rec.error}." if rec.error else ""
    return {"text": f"Recording finished: {secs:.1f} s, {len(rec.frames)} frames captured ({kept} in the GIF, {size[0]}x{size[1]}, "
                    f"{len(data) // 1024} KB). The GIF is attached; a copy is saved at {path}.{note}",
            "images": [{"data": base64.b64encode(data).decode("ascii"), "mimeType": "image/gif"}]}


def call(name, args, timeout=30):
    global _cur, _done
    args = args or {}
    try:
        import PIL  # noqa: F401
    except ImportError:
        raise RuntimeError("Recording needs the Pillow package (it ships with the LuauPilot app).")
    with _lock:
        if _done and time.time() - _done[0] > KEEP_RESULT_S:
            _done = None
        if _cur and not _cur.thread.is_alive():          # ended on its own (time limit or error)
            _done, _cur = (time.time(), _cur), None
        if name == "record_start":
            if _cur:
                raise RuntimeError("A recording is already running: send record_stop first.")
            _done = None
            rec = _Rec(_clamp(args.get("fps"), 1, MAX_FPS, DEFAULT_FPS), _clamp(args.get("max_seconds"), 1, MAX_SECONDS, DEFAULT_SECONDS),
                       _clamp(args.get("width"), 160, MAX_WIDTH, DEFAULT_WIDTH), "screen" if str(args.get("region")) == "screen" else "studio")
            if rec.region == "studio":
                _studio_rect() if GRAB is _grab else None      # fail now with a clear message, not later
            rec.thread.start()
            _cur = rec
            return {"text": f"Recording started ({rec.fps} fps, up to {rec.seconds} s, {rec.region}). Send the command you want to watch, "
                            "then record_stop.", "images": []}
        # record_stop
        rec = _cur or (_done[1] if _done else None)
        if rec is None:
            raise RuntimeError("No recording to stop: send record_start first.")
        _cur = _done = None
    return _finish(rec)
