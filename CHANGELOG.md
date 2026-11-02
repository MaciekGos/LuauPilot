# Changelog

## Alpha 0.03
- The chat tab no longer falls asleep when you switch tabs. While a session runs (setting "Keep this tab awake", on by default): the tab plays an inaudible tone and holds a Web Lock, so Chrome/Edge do not throttle, freeze or put it to sleep; the background worker marks the tab "do not discard"; and `requestAnimationFrame` - which the browser stops completely in a background tab and which chat sites use to draw streamed text - falls back to a timer while the tab is really hidden (frames that were waiting when the tab went to the background are run too). The tab may show a speaker icon while this is on.
- Smaller exe: the unused HTML mini chat is removed together with pywebview, pythonnet (the .NET bridge) and bottle - the Tk mini chat (the one that is used) stays - and the unused Pillow AVIF/WebP/ICC plugins are no longer bundled. `build.bat` no longer installs pywebview (it needs pythonnet, which often has no wheel for a new Python and made the build fail), writes every step to `installer\build-log\` and shows the last lines of the failing step.
- Fix: LuauPilot sometimes ended the task although DeepSeek had just sent a command (often after switching browser tabs, but not only then). A reply that was read as a plain answer while the page showed it only partly stayed "answered" for good, so the command that appeared a moment later was ignored. Now such a reply is read again when its text changes, and the command runs.
- Background tabs: a browser tab in the background renders the site only now and then, so "no change for a while" proves little there. While the tab is hidden, a reply without a complete command needs 20 s without activity and 30 s without text change before it counts as finished (a complete command still runs after about 2 s). After you switch back, LuauPilot waits a few seconds so the page can catch up first.

## Alpha 0.02
- **Renamed to LuauPilot** (new name and logo everywhere: README, terms, installer, desktop app, browser extension, bridge console, Studio plugin). The model's reply tag is now `[LuauPilot]` (the old `[LuaPilot]` is still understood). Kept on purpose so updates and existing games keep working: the GitHub repository URL, the install and data folders (`%APPDATA%\LuaPilot`, `~/LuaPilot/Guide`, `%LOCALAPPDATA%\Programs\LuaPilot`), the exe and file names, the registry keys and the in-game `ServerStorage.LuaPilot.Memory`. They change together with the GitHub repository rename. The installer shows "LuauPilot" in shortcuts and in Apps & features and removes shortcuts of the old name.
- Editing while Studio is in Play mode: every command that has a `datamodel_type` now defaults to the Edit datamodel (not only execute_luau). If an edit still fails and Studio really is playing, the playtest is stopped once, the edit is repeated and the AI is told.
- Assets and Blender first: when the catalog is allowed or Blender is connected the AI must use them before building an object from Parts.
- New commands `record_start` / `record_stop`: a short GIF recording of the Studio window (5 fps, 20 s default, 30 s max, under about 1.5 MB), so the AI can watch motion, animations and gameplay and not only still screenshots. Needs Pillow in the bridge (already part of the app build).
- Per-game workspace: new command `game_workspace`. Before working on a game the AI copies the project documents (rules, style guide, assets, known issues, design handbook and reference pictures) into a temporary folder for that game (`%TEMP%\\LuaPilot\\Games\\<game>\\Guide`) and adapts the copy to it: a short `GAME.md` profile, style sections, asset lists. `style_guide` and `reference_images` read the copy while it is open; the master files in `~/LuaPilot/Guide` are never changed. Reopening the same game keeps its adaptations (`fresh` copies the master again), `reset` and `close` are available, and copies older than 14 days are deleted. Build fix: `build.bat` now stops with a visible error message and the spec no longer edits the PyInstaller analysis result.
- **Note: LuaPilot is now LuauPilot.** The project was renamed because LuaPilot.com already exists and provides a very similar product. The repository, application and branding are being updated to the new name, so the GitHub repository and some file names still say LuaPilot for now. The project itself is not discontinued. The notice is shown in the README, terms, installer, desktop app, browser extension and the bridge console.
- Smaller download: unused GUI backends (Qt, GTK, Cocoa, CEF), setuptools, numpy and Tcl locale/timezone data are no longer bundled, and the installer payload is compressed with LZMA instead of Deflate.
- Speed: a reply that ends in one complete command block is now noticed after about 2 s instead of 9 s or more (prose, unfinished commands and DSML keep the long calm period). The bridge no longer asks Roblox Studio for its command list on every request (at most every 2 minutes, or when forced after an unknown-command error). The send limits are untouched (6 s between sends, 5 per minute, back-off ladder), so "Messages too frequent" protection is unchanged.
- One-time feedback question after about 1 hour of active use (the bridge counts only time with a connected extension and a recent command or running chat). It asks whether you had problems or whether your DeepSeek account was blocked. "No" thanks you and asks you to share your opinion on GitHub Issues; "Yes" says sorry, asks you to describe exactly what happened there, and both stress that knowing everything is OK is just as valuable. It shows in three places that stay in sync: a small corner card on the chat page (only while LuauPilot is idle, never a modal), one Windows notification (skipped when the app window is in front) and a slim bar in the desktop app. "Later" postpones it by 3 more hours of use, at most 2 questions in total, any answer ends it for good. Turn it off with {"feedback_prompt": false} in %APPDATA%\\LuaPilot\\settings.json. State file: %APPDATA%\\LuaPilot\\feedback.json.

## 2.0.3
- Mini chat: the built-in Tk window stays the default. An experimental HTML version (pywebview / WebView2, enable with "mini_kind": "web" in settings.json) exists in the style of the chat box of the AI site, with the Tk window as automatic fallback when WebView2 or pywebview is missing. Plugin link moved to port 17615 (17614 belongs to the mini chat API).
- Mini chat (Tk version) restyled like the chat box of the AI site: big rounded input card with a placeholder, round buttons (open site, stop, answer, blue send arrow), focus glow, fade-in, smooth expand, pulsing status dot. Enter sends, Shift+Enter adds a line.
- Animations: smooth button colour transitions and window fade-in in the app; pages slide in and the current step pulses in the installer.
- Housekeeping: logs, exported models and stored chat notes older than 4 days (counted from the newest entry, not from today) are deleted automatically at start and every 6 hours. Your Guide folder is never touched.
- Blender mode: the AI must model anything with shape in Blender (real geometry, bevels, details, several materials), not from Parts; with the catalog off it is Blender-only. Models and their textures (baked PNG, FBX with embedded textures) go to a temp folder inside LuauPilot's own files (new command models_folder). New command models_import uploads them to Roblox with your own Open Cloud API key (app Settings > Roblox upload) and a small LuauPilot Studio plugin (Settings > Install Studio plugin) loads them into Workspace > LuauPilot Imports. Studio has no public API to import a local FBX, hence the upload. Without a key the AI asks for a manual Import 3D. Bridge log: Blender's own verbose lines are no longer stored.
- Coming back to a chat that needed Blender: the extension remembers it per chat, re-checks the connection, reconnects, and pauses with instructions if Blender is not running.
- Installer is now LuauPilot's own dark setup (windows.exe) with Uninstall/Reinstall; the app checks GitHub releases by publication date and updates itself.
- LuauPilot's own messages (results, errors, instructions, screenshots) are hidden from the chat; the command chip on the assistant turn shows what ran.
- Stop button in the chat bar while LuauPilot works. The on/off switch left the bar (it stays in the extension popup). The message box is locked while LuauPilot works; press Stop to write.
- The model's own tool-call tags (DSML) are now read as a command and run; any leftover text is hidden.
- Editing during a playtest: the AI is told to keep using the Edit datamodel while the game runs.
- Screenshots are labelled as tool output (not the user's photo) and are not shown in the chat. The preview keeps the last 10; the full-screen view browses them with arrows and a strip.
- Starting a session asks: allow the Roblox catalog? use Blender? The AI is told to prefer catalog assets or Blender over plain Parts when allowed, and cannot use them when not.
- Optional Blender connection (per session, off by default) through the same MCP mechanism as Studio (mcp-for-blender via uv, telemetry disabled), with an in-page setup guide when it does not connect.
- New project documents the AI reads at the start of a session and on request: AGENT_INSTRUCTIONS, STYLE_GUIDE, GAME_DESIGN (long handbook in chapters), ASSETS, KNOWN_ISSUES and a REFERENCES folder of example pictures (oldcity.png, mainmenu.png, ...). New commands style_guide and reference_images. Files live in an editable folder (Guide button in the app).
- After visual work the AI must check at least four views (wide, two at player height, close-up) and name the weakest one.
- Installer shows the full terms on a page that must be accepted (generated from TERMS.md by make_terms.py).
- Desktop app: two-row button layout, mini chat redesigned (rounded, no system title bar, pin, drag, resize), "Open DeepSeek" button and queued sending when the page is not open, new multi-size icon (taskbar uses the 128 and 48 px versions).

## 2.0.2
- Phosphor Icons in the extension (chips, bar, popup) and in the desktop app buttons.

## 2.0.1
- Fixed the white circle logo (the white wordmark was built from transparency only).
- DeepSeek: a refused message is never re-sent in a burst; every failed send backs off (15 s, 30 s, 60 s ... 5 min), survives page reloads, and send() no longer re-clicks after a "Messages too frequent" notice.
- Works while the browser tab is in the background: the page is told it is visible, timers are driven from the background worker, and a pulse keeps the agent loop running.
- Parser accepts command markers anywhere in the text (one-line blocks too).
- Images: screen_capture is no longer refused; the screenshot is attached when the chat accepts images, otherwise the AI is told it could not be attached.
- New commands answered by the bridge: catalog_search and catalog_images (Roblox Creator Store search with thumbnails).
- Running commands have animations; bar menu has a Diagnostics panel.
- Desktop app: Mini chat (always-on-top box with Send/Stop and the AI's answer). The bridge only accepts connections from the extension (web pages are refused).

## 2.0.0
- New project: LuauPilot. Bridge, browser extension and desktop app were written from scratch.
- DeepSeek is the only supported chat site; Roblox Studio is the only MCP connection.
- New agent loop: history is never executed, every reply is answered at most once, executed commands are remembered across reloads.
- New send governor (spacing, per-minute cap, adaptive slow-down) and a recovery ladder for "Messages too frequent": reload, longer wait, fresh chat, then a visible stop with countdown.
- Loop guards: the same command 4 times in a row, or repeated unreadable replies, stop the agent.
- Screenshot preview can be shown or hidden; clicking it opens a full-screen lightbox.
- LuauPilot ON/OFF switch in the chat bar; redesigned toolbar popup with a power switch and bridge connect/disconnect.
- Desktop app: settings for auto-opening the AI agent and Roblox Studio at startup; the Extension button copies the folder path and explains how to load it.
