# SPDX-License-Identifier: MIT
"""Project documents and reference pictures for the AI, answered by the bridge itself.

    style_guide       - how to work, visual style, approved assets, known issues, the long design handbook
    reference_images  - the user's own example pictures (REFERENCES/oldcity.png, mainmenu.png, ...)

The documents are plain files the user can edit. Defaults ship in ./guide; on first run they are copied
to the user's own folder (LP_GUIDE_DIR, default ~/LuaPilot/Guide) and from then on that copy is used, so
edits survive updates and the folder is writable. Files are never overwritten.
"""
import base64
import datetime
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
BUNDLED = os.path.join(HERE, "guide")
USER = os.environ.get("LP_GUIDE_DIR") or os.path.join(os.path.expanduser("~"), "LuaPilot", "Guide")
DOCS = {"agent": "AGENT_INSTRUCTIONS.md", "style": "STYLE_GUIDE.md", "assets": "ASSETS.md",
        "issues": "KNOWN_ISSUES.md", "design": "GAME_DESIGN.md", "game": "GAME.md"}
COPIED = [v for k, v in DOCS.items() if k != "game"]       # what a game workspace gets a private copy of
GAMES = os.environ.get("LP_GAME_TMP") or os.path.join(tempfile.gettempdir(), "LuaPilot", "Games")
ACTIVE_FILE = os.path.join(GAMES, "active.json")
KEEP_DAYS = 14
MAX_REF_FILE = 5_000_000
MAX_REF_TOTAL = 60_000_000
GAME_TEMPLATE = """# Game: {name}
Opened: {date}    Place id: {pid}

(Fill this in from the user's task and the project. Keep it short - under 40 lines. Every start read shows it.)

- Genre / fantasy:
- Camera and controls:
- Map size and scale:
- Art style and palette (from STYLE_GUIDE, or what differs for this game):
- UI style:
- Sound and mood:
- Core loop:
- Out of scope:
"""
SECTIONS = ["rules", "structure", "colors", "ui", "assets", "sounds", "images", "approved"]
IMG_EXT = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
MAX_IMG = 900_000
MAX_DOC = 14_000
PICTURES = [("palette", "Colour palettes (Dusk, Meadow, Neon) with hex values"),
            ("ui-layout", "UI layout: 8 px grid, safe zone, button sizes"),
            ("folder-structure", "Recommended project structure"),
            ("lighting", "Lighting mood presets: Day, Dusk, Night"),
            ("asset-consistency", "Assets that match the style vs assets that clash")]

TOOLS = [
    {"name": "style_guide",
     "description": "Project documents: how to work, the visual style, approved/rejected assets, known issues, and a long "
                    "game-design handbook in chapters. Without arguments returns the essentials and lists what else exists.",
     "inputSchema": {"type": "object", "properties": {
         "doc": {"type": "string", "enum": ["start", "agent", "style", "assets", "issues", "design", "sounds", "game"],
                 "description": "which document (default start)"},
         "section": {"type": "string", "description": "style: rules|structure|colors|ui|assets|sounds|images|approved; "
                                                       "design: a chapter number (7), a range (7-9) or a word from the title (lighting)"},
         "images": {"type": "boolean", "description": "attach the guide's example pictures (default false)"}}}},
    {"name": "game_workspace",
     "description": "Per-game working copy of the project documents (rules, style, assets, known issues, design handbook, reference "
                    "pictures) in a temporary folder, so they can be adapted to ONE game without touching the user's master files. "
                    "action open (default): create it for this game (game = the game's name) and copy the documents in. "
                    "adapt: change a document of the copy (doc, text, optional section). status | reset (copy the master again) | close.",
     "inputSchema": {"type": "object", "properties": {
         "action": {"type": "string", "enum": ["open", "status", "adapt", "reset", "close"], "description": "default open"},
         "game": {"type": "string", "description": "open: the name of this game (the place name or what the user calls it)"},
         "place_id": {"type": "string", "description": "open: the Roblox place id, if known"},
         "fresh": {"type": "boolean", "description": "open: throw away an earlier copy of this game and copy the master again"},
         "doc": {"type": "string", "enum": ["game", "agent", "style", "assets", "issues", "design"], "description": "adapt: which document of the copy"},
         "section": {"type": "string", "description": "adapt: replace this section (a '## heading' of the document) instead of adding a new block"},
         "text": {"type": "string", "description": "adapt: the new text (game: the whole profile)"}}}},
    {"name": "reference_images",
     "description": "The user's reference pictures for how things should look (files like oldcity.png, mainmenu.png). "
                    "No arguments: lists the names. names or query: returns the matching pictures (max 6) as images.",
     "inputSchema": {"type": "object", "properties": {
         "list": {"type": "boolean", "description": "only list the available names"},
         "names": {"type": "array", "items": {"type": "string"}, "description": "picture names without extension"},
         "query": {"type": "string", "description": "a word to look for in the names, e.g. city"}}}},
]
NAMES = {t["name"] for t in TOOLS}


def ensure_user_dir():
    """Copy missing default files to the user's folder. Never overwrites. Returns the folder path."""
    try:
        for root, _dirs, files in os.walk(BUNDLED):
            rel = os.path.relpath(root, BUNDLED)
            if rel.split(os.sep)[0] in ("images", "__pycache__"):
                continue
            dest = os.path.join(USER, rel) if rel != "." else USER
            os.makedirs(dest, exist_ok=True)
            for f in files:
                if f.endswith((".py", ".pdf")):
                    continue
                target = os.path.join(dest, f)
                if not os.path.exists(target):
                    shutil.copyfile(os.path.join(root, f), target)
        os.makedirs(os.path.join(USER, "REFERENCES"), exist_ok=True)
        return USER
    except OSError:
        return BUNDLED


def _slug(name):
    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")[:40] or "game"


def _active():
    """{"slug", "name"} of the game workspace that is open, or None."""
    try:
        with open(ACTIVE_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
        if os.path.isdir(os.path.join(GAMES, data["slug"], "Guide")):
            return data
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None


def _master():
    return USER if os.path.isdir(USER) else BUNDLED


def _dir():
    act = _active()
    return os.path.join(GAMES, act["slug"], "Guide") if act else _master()


def _read(rel):
    for base in ((_dir(), USER, BUNDLED) if rel != DOCS["game"] else (_dir(),)):
        path = os.path.join(base, rel)
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read()
    if rel == DOCS["game"]:
        raise RuntimeError("No game workspace is open yet: call game_workspace (action open, game = the game's name) first.")
    raise RuntimeError(f"{rel} is missing from the guide folder ({_dir()}).")


def _cap(text, n=MAX_DOC):
    text = text.strip()
    return text if len(text) <= n else text[:n] + "\n...[cut: ask for a smaller section]"


def _sections(text):
    head, parts, cur = [], {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip().lower()
            parts[cur] = []
        elif cur is None:
            head.append(line)
        else:
            parts[cur].append(line)
    return "\n".join(head).strip(), {k: "\n".join(v).strip() for k, v in parts.items()}


_CH = re.compile(r"^#{1,2}\s+(\d+)\.\s+(.*\S)\s*$")


def _chapters(text):
    """[(number, title, body)] for the numbered chapters of the design handbook."""
    out, cur = [], None
    for line in text.splitlines():
        m = _CH.match(line)
        if m:
            cur = [int(m.group(1)), m.group(2), []]
            out.append(cur)
        elif cur is not None:
            cur[2].append(line)
    return [(n, t, "\n".join(b).strip()) for n, t, b in out]


def _design(section):
    chapters = _chapters(_read(DOCS["design"]))
    if not section:
        lines = [f"{n}. {t}" for n, t, _ in chapters]
        return ("Game design and visual handbook - chapters. Ask again with doc \"design\" and section = a number (7), "
                "a range (7-9) or a word from the title (lighting).\n" + "\n".join(lines))
    sec = str(section).strip().lower()
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", sec)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        pick = [c for c in chapters if lo <= c[0] <= hi]
    elif sec.isdigit():
        pick = [c for c in chapters if c[0] == int(sec)]
    else:
        pick = [c for c in chapters if sec in c[1].lower()]
    if not pick:
        raise RuntimeError("no chapter matches; call style_guide with doc \"design\" and no section to see the list")
    return _cap("\n\n".join(f"# {n}. {t}\n{b}" for n, t, b in pick), 18_000)


def _refs():
    base = os.path.join(_dir(), "REFERENCES")
    out = {}
    for root, _d, files in os.walk(base):
        for f in sorted(files):
            stem, ext = os.path.splitext(f)
            if ext.lower() in IMG_EXT:
                rel = os.path.relpath(os.path.join(root, f), base).replace(os.sep, "/")
                out[os.path.splitext(rel)[0]] = os.path.join(root, f)
    return out


def _load_image(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as fh:
        data = fh.read()
    mime = IMG_EXT[ext]
    if len(data) > MAX_IMG:
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(data)).convert("RGB")
            im.thumbnail((1280, 1280))
            buf = io.BytesIO()
            im.save(buf, "JPEG", quality=82)
            data, mime = buf.getvalue(), "image/jpeg"
        except Exception:
            return None
        if len(data) > MAX_IMG:
            return None
    return {"data": base64.b64encode(data).decode("ascii"), "mimeType": mime}


def _reference_images(args):
    refs = _refs()
    if not refs:
        return {"text": "There are no reference pictures yet. The user can add them to the REFERENCES folder of the "
                        f"guide ({os.path.join(_dir(), 'REFERENCES')}), named after what they show (oldcity.png, mainmenu.png). "
                        "Continue with the written style guide.", "images": []}
    names, query = args.get("names") or [], str(args.get("query") or "").strip().lower()
    if args.get("list") or not (names or query):
        return {"text": "Reference pictures (ask for them with names or query):\n" + "\n".join(f"- {k}" for k in sorted(refs)), "images": []}
    chosen = []
    for n in names:
        n = str(n).strip().lower().rsplit(".", 1)[0] if str(n).lower().endswith(tuple(IMG_EXT)) else str(n).strip().lower()
        hit = [k for k in refs if k.lower() == n or k.lower().rsplit("/", 1)[-1] == n]
        chosen += hit or [k for k in refs if n and n in k.lower()]
    if query:
        chosen += [k for k in refs if query in k.lower()]
    seen, ordered = set(), []
    for k in chosen:
        if k not in seen:
            seen.add(k)
            ordered.append(k)
    if not ordered:
        return {"text": "No picture matches. Available:\n" + "\n".join(f"- {k}" for k in sorted(refs)), "images": []}
    images, lines, skipped = [], [], []
    for k in ordered[:6]:
        img = _load_image(refs[k])
        if img:
            images.append(img)
            lines.append(f"Picture {len(images)}: {k}")
        else:
            skipped.append(k)
    text = "Attached in this order:\n" + "\n".join(lines) if lines else "None of the matching pictures could be attached."
    if skipped:
        text += f"\nToo large to attach (ask the user to shrink them): {', '.join(skipped)}"
    if len(ordered) > 6:
        text += f"\n{len(ordered) - 6} more match; narrow the query to see them."
    return {"text": text, "images": images}


def _example_pictures(body):
    images = []
    for stem, cap in PICTURES:
        path = os.path.join(BUNDLED, "images", stem + ".png")
        if os.path.isfile(path) and os.path.getsize(path) < MAX_IMG:
            with open(path, "rb") as fh:
                images.append({"data": base64.b64encode(fh.read()).decode("ascii"), "mimeType": "image/png"})
            body += f"\nPicture {len(images)}: {cap}"
    return body, images


# ── per-game workspace ────────────────────────────────────────────────────
# Before each game the documents are copied to a temporary folder and adapted there; the user's master
# files (ensure_user_dir) are never changed by this.
def _stamp(text, name):
    note = f"<!-- LuauPilot game copy for \"{name}\", {datetime.date.today().isoformat()}. Adapt this copy; the master stays untouched. -->\n"
    return text if text.startswith("<!-- LuauPilot game copy") else note + text


def _copy_master(dest, name):
    src = _master()
    copied, total = [], 0
    os.makedirs(dest, exist_ok=True)
    for f in COPIED:
        path = os.path.join(src, f)
        if not os.path.isfile(path):
            path = os.path.join(BUNDLED, f)
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            with open(os.path.join(dest, f), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(_stamp(text, name))
            copied.append(f)
    os.makedirs(os.path.join(dest, "REFERENCES"), exist_ok=True)
    refs = os.path.join(src, "REFERENCES")
    if os.path.isdir(refs):
        for root, _d, files in os.walk(refs):
            for f in files:
                p = os.path.join(root, f)
                size = os.path.getsize(p)
                if os.path.splitext(f)[1].lower() not in IMG_EXT or size > MAX_REF_FILE or total + size > MAX_REF_TOTAL:
                    continue
                target = os.path.join(dest, "REFERENCES", os.path.relpath(p, refs))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(p, target)
                total += size
                copied.append("REFERENCES/" + os.path.relpath(p, refs).replace(os.sep, "/"))
    return copied


def _purge_old(keep):
    try:
        for entry in os.listdir(GAMES):
            p = os.path.join(GAMES, entry)
            if entry != keep and os.path.isdir(p) and time.time() - os.path.getmtime(p) > KEEP_DAYS * 86400:
                shutil.rmtree(p, ignore_errors=True)
    except OSError:
        pass


def _set_active(slug, name):
    os.makedirs(GAMES, exist_ok=True)
    with open(ACTIVE_FILE, "w", encoding="utf-8") as fh:
        json.dump({"slug": slug, "name": name}, fh)


def _adapted(dest):
    """Documents of the copy that differ from the master (what has been adapted)."""
    out = []
    for f in COPIED + [DOCS["game"]]:
        p = os.path.join(dest, f)
        if not os.path.isfile(p):
            continue
        if f == DOCS["game"]:
            out.append(f)
            continue
        try:
            with open(p, encoding="utf-8", errors="replace") as a, open(os.path.join(_master(), f), encoding="utf-8", errors="replace") as b:
                if _stamp(b.read(), "").split("\n", 1)[-1].strip() != a.read().split("\n", 1)[-1].strip():
                    out.append(f)
        except OSError:
            out.append(f)
    return out


def _replace_section(text, section, body):
    pat = re.compile(r"(^##\s+" + re.escape(section.strip()) + r"\s*$)(.*?)(?=^##\s|\Z)", re.S | re.M | re.I)
    if not pat.search(text):
        return None
    return pat.sub(lambda m: m.group(1) + "\n" + body.strip() + "\n\n", text, count=1)


def _workspace(args):
    action = str(args.get("action") or "open").lower()
    act = _active()
    if action == "open":
        name = str(args.get("game") or "").strip()
        if not name:
            raise RuntimeError("game is required: the name of this game (the place name or what the user calls it)")
        slug = _slug(name)
        dest = os.path.join(GAMES, slug, "Guide")
        fresh = bool(args.get("fresh"))
        if os.path.isdir(dest) and not fresh:
            _set_active(slug, name)
            note = "An earlier copy of this game was found - its adaptations are kept (fresh: true copies the master again)."
        else:
            if os.path.isdir(dest):
                shutil.rmtree(dest, ignore_errors=True)
            copied = _copy_master(dest, name)
            with open(os.path.join(dest, DOCS["game"]), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(GAME_TEMPLATE.format(name=name, date=datetime.date.today().isoformat(), pid=args.get("place_id") or "unknown"))
            _set_active(slug, name)
            note = "Copied %d files from the master guide into the temporary folder." % len(copied)
        _purge_old(slug)
        return {"text": (f"Game workspace \"{name}\" is open.\nFolder: {dest}\n{note}\n\n"
                         "NEXT: (1) fill in the game profile: game_workspace action adapt, doc game, text = the whole GAME.md. "
                         "(2) Adapt what must differ for THIS game: action adapt with doc style (section colors, ui, sounds, ...), "
                         "assets, issues, design or agent. From now on style_guide and reference_images read this copy, and the master "
                         "files stay untouched."), "images": []}
    if not act:
        if action == "close":
            return {"text": "No game workspace was open.", "images": []}
        raise RuntimeError("No game workspace is open: call game_workspace with action open and game = the game's name.")
    dest = os.path.join(GAMES, act["slug"], "Guide")
    if action == "status":
        return {"text": f"Open game: {act['name']}\nFolder: {dest}\nAdapted documents: {', '.join(_adapted(dest)) or 'none yet'}", "images": []}
    if action == "close":
        try:
            os.remove(ACTIVE_FILE)
        except OSError:
            pass
        return {"text": f"Closed \"{act['name']}\". The copy stays in {dest} for {KEEP_DAYS} days; style_guide reads the master again.", "images": []}
    if action == "reset":
        shutil.rmtree(dest, ignore_errors=True)
        copied = _copy_master(dest, act["name"])
        with open(os.path.join(dest, DOCS["game"]), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(GAME_TEMPLATE.format(name=act["name"], date=datetime.date.today().isoformat(), pid="unknown"))
        return {"text": f"\"{act['name']}\" copied again from the master ({len(copied)} files); the adaptations are gone.", "images": []}
    if action == "adapt":
        doc = str(args.get("doc") or "game").lower()
        text = str(args.get("text") or "")
        if doc not in DOCS:
            raise RuntimeError("doc must be one of: " + ", ".join(DOCS))
        if not text.strip():
            raise RuntimeError("text is required")
        if len(text) > 20000:
            raise RuntimeError("text is too long (max 20000 characters); split it over several adapt calls")
        path = os.path.join(dest, DOCS[doc])
        old = open(path, encoding="utf-8", errors="replace").read() if os.path.isfile(path) else ""
        section = str(args.get("section") or "").strip()
        if doc == "game" and not section:
            new, how = text.strip() + "\n", "replaced"
        else:
            new = _replace_section(old, section, text) if section else None
            how = "section replaced"
            if new is None:
                new = old.rstrip() + f"\n\n## Game-specific: {section or 'adaptation'}\n{text.strip()}\n"
                how = "added as a new block"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new)
        os.utime(os.path.join(GAMES, act["slug"]))
        return {"text": f"{DOCS[doc]} ({act['name']}): {how}.", "images": []}
    raise RuntimeError("action must be one of: open, status, adapt, reset, close")


def call(name, args, timeout=30):
    args = args or {}
    if name == "game_workspace":
        return _workspace(args)
    if name == "reference_images":
        return _reference_images(args)
    doc = str(args.get("doc") or ("style" if args.get("section") else "start")).lower()
    section = args.get("section")
    images = []
    if doc == "start":
        refs = _refs()
        design = _chapters(_read(DOCS["design"]))
        act = _active()
        if act:
            try:
                profile = "# This game: %s (adapted copy of the guide in use)\n%s\n\n" % (act["name"], _cap(_read(DOCS["game"]), 3000))
            except RuntimeError:
                profile = ""
        else:
            profile = ("# No game workspace is open\nBefore working on a game, call game_workspace (action open, game = the game's name): it copies "
                       "these documents to a temporary folder and lets you adapt them to this one game.\n\n")
        body = profile + "\n\n".join([
            _cap(_read(DOCS["agent"]), 6000),
            _cap(_read(DOCS["style"]), 9000),
            "# Approved and rejected assets (the user's list)\n" + _cap(_read(DOCS["assets"]), 3000),
            "# Known issues\n" + _cap(_read(DOCS["issues"]), 2000),
            "# More\n- style_guide doc \"design\": the long game-design handbook, %d chapters (genre, map size, assets, lighting, UI, multi-view review...). Read the chapters that match the task.\n"
            "- reference_images: %s\n- Your documents live in: %s" % (
                len(design), (f"{len(refs)} reference pictures: " + ", ".join(sorted(refs)[:30])) if refs else "none yet",
                _dir())])
    elif doc == "design":
        body = _design(section)
    elif doc in ("style", "sounds"):
        head, parts = _sections(_read(DOCS["style"]))
        want = "sounds" if doc == "sounds" else str(section or "all").lower()
        if want != "all" and want not in parts:
            raise RuntimeError(f"section must be one of: all, {', '.join(parts)}")
        if want == "all":
            body = _cap(_read(DOCS["style"]))
        else:
            body = f"## {want}\n{parts[want]}"
            if parts.get("approved") and want != "approved":
                body += f"\n\n## approved (overrides the above)\n{parts['approved']}"
        if want == "images" or args.get("images"):
            body, images = _example_pictures(body)
    elif doc in DOCS:
        body = _cap(_read(DOCS[doc]))
    else:
        raise RuntimeError("doc must be one of: start, agent, style, assets, issues, design, sounds, game")
    if args.get("images") and not images:
        body, images = _example_pictures(body)
    return {"text": body.strip(), "images": images}
