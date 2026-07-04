# mockmeup

Turn any app or project into a **premium showcase mockup / poster** — a great background, your
screenshots in nice device frames, and the app name + slogan. The kind of image you'd put on a
README hero, Product Hunt, a landing page, or a social post.

## Invoke

```
/mockmeup                     # showcase the project in the current directory
/mockmeup <path-to-project>   # showcase a specific project
/mockmeup <path> og square    # also render extra sizes
```

Or just ask: *"make a mockup for this app"*, *"I need a poster to show off this project"*.

## How it works

1. **Detects** the project (type, brand color, logo, name, tagline, features) and whether it can run.
2. **Gets screenshots**, three ways, automatically:
   - **A.** If a `Screenshots/` folder exists → uses those.
   - **B.** Else if the app is runnable → launches it, screenshots it with Playwright, checks the
     shots aren't blank, saves them into `screenshots/`, and continues.
   - **C.** Else (it's a skill / library / CLI / not runnable) → synthesizes a conceptual mockup from
     the project's info: a terminal window, feature cards, logo, and generated key art.
3. **Designs** a poster (atmospheric background + framed screenshots + typographic text) using a
   curated design system that avoids generic "AI slop".
4. **Renders** a crisp retina PNG (default sizes: 4:5 social `1080×1350` and OG `1200×630`).
5. **Reviews** the result and offers variations.

Outputs land in `<project>/mockups/`. Captured screenshots land in `<project>/screenshots/`.

## Layout

```
mockmeup/
├── SKILL.md                     # orchestration (the brain)
├── scripts/
│   ├── detect_project.py        # classify project + pull name/tagline/features/logo/color
│   ├── capture_app.py           # Playwright: screenshot a running web app (desktop + mobile)
│   ├── check_screenshots.py     # reject blank/low-content/too-small shots; suggest frame
│   └── render_poster.py         # Playwright: render poster HTML → retina PNG at any size(s)
├── references/
│   ├── backgrounds.md           # premium CSS background recipes (aurora, mesh, grid, gold, …)
│   ├── frames.md                # phone / browser / laptop / terminal / card frames + arrangement
│   └── layout.md                # per-size composition, type scale, color, anti-slop checklist
├── assets/
│   └── poster_template.html     # a ready 4:5 poster scaffold with {{TOKENS}}
└── README.md
```

## Requirements (already satisfied on this machine)

- **Playwright** (Python) + the on-disk Chromium at
  `…/ms-playwright/chromium-1187/chrome-win/chrome.exe` — used for both app capture and HTML→PNG.
- **Pillow** — used to validate screenshots.
- No network required for rendering; Google Fonts load at render time if available.

## Notes

- Output sizes: `social` (1080×1350), `og`/`wide` (1200×630), `square` (1080×1080),
  `hero` (1920×1080), `story` (1080×1920), or any `WxH`.
- Backgrounds are generated locally (offline, deterministic). AI-generated or stock-photo backgrounds
  could be added later as alternate providers.
