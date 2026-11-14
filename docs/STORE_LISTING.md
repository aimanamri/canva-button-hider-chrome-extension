# Chrome Web Store listing (draft)

**Name:** Canva Button Hider
**Summary (132 max):** Hide the "Send to teacher" button on Canva Education designs with one click, so you never submit by accident.
**Category:** Productivity

**Description**
Canva for Education puts "Send to teacher" right beside Share. One stray click can hand in unfinished work.
Canva Button Hider hides that button and brings it back whenever you want.

- One-click toggle from the popup, applied instantly to open tabs
- Keyboard shortcut: Alt+Shift+H
- OFF badge on the toolbar icon when paused
- Light and dark mode

**Privacy:** Stores one setting (on/off) in Chrome sync storage. No network requests, no analytics, no data collected. Runs only on canva.com/design pages.

**Permission justification**
- `storage`: remember the on/off setting.
- Host `https://www.canva.com/design/*`: find and hide the button on design pages.

**Assets:** icon `extension/icons/icon128.png`; screenshots to upload at 1280x800 (take from a real Canva page); build zip with `scripts/package.sh`.
**Fee:** a one-time US$5 developer registration is required to publish.
