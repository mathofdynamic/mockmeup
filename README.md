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
3. **Picks a theme** from a library of **24 premium themes** via `scripts/pick_theme.py`, which rotates
   so you get a *different* look every time — it excludes themes recently used for this project and
   globally, then the model picks the best mood-fit for the app. When several sizes are rendered in one
   run, **each size gets its own distinct theme**.
4. **Designs** a poster (atmospheric background + framed screenshots + typographic text) on top of the
   chosen theme, using a curated design system that avoids generic "AI slop".
5. **Renders** a crisp retina PNG (default sizes: 4:5 social `1080×1350` and OG `1200×630`).
6. **Reviews** the result, records the themes used (so the next run rotates away), and offers variations.

Outputs land in `<project>/mockups/`. Captured screenshots land in `<project>/screenshots/`.

## Theme library (24 premium themes)

Every theme in `assets/themes.css` ships a full palette, an atmospheric CSS background stack, frame
styling, and **both a Latin and a Persian/RTL font pairing** — all exposed as the same CSS custom
properties, so one poster template works with any theme (just add `class="poster theme-<id>"`).

- **Dark:** aurora-noir · obsidian-gold · blueprint · glass-dark · monochrome-ink · deep-forest ·
  midnight-indigo · graphite-tech · royal-slate · emerald-boardroom · burgundy-prestige · copper-dusk ·
  spotlight-stage · sapphire-depth
- **Light:** editorial-paper · swiss-minimal · glass-light · champagne-studio · arctic-frost ·
  terracotta-editorial · persian-geometry · pearl-gradient · nordic-calm
- **Either:** duotone-studio

Themes are indexed with mood `tags` in `references/themes/catalog.json`. Rotation state persists in
`theme_history.json` (git-ignored). All 24 are premium/professional — variety comes from color,
typography, texture, and composition, not gimmicks.

```bash
# shortlist themes for a project (excludes recently used), pick N distinct, one per size:
python scripts/pick_theme.py shortlist --project "My App" --count 2 --tags corporate,cool --mode dark
# after rendering, record what you used so the next run rotates away:
python scripts/pick_theme.py record --project "My App" --theme royal-slate --theme obsidian-gold
```

## Layout

```
mockmeup/
├── SKILL.md                     # orchestration (the brain)
├── scripts/
│   ├── detect_project.py        # classify project + pull name/tagline/features/logo/color
│   ├── capture_app.py           # Playwright: screenshot a running web app (desktop + mobile)
│   ├── check_screenshots.py     # reject blank/low-content/too-small shots; suggest frame
│   ├── pick_theme.py            # theme rotation: shortlist (excludes recent) + record
│   └── render_poster.py         # Playwright: render poster HTML → retina PNG at any size(s)
├── references/
│   ├── themes/
│   │   └── catalog.json         # index of the 24 themes (id, mode, mood tags)
│   ├── backgrounds.md           # extra CSS background recipes (aurora, mesh, grid, gold, …)
│   ├── frames.md                # frames + multi-shot arrangement (≥55%-visible rule)
│   └── layout.md                # per-size composition archetypes, type scale, anti-slop checklist
├── assets/
│   ├── themes.css               # the 24-theme library (palette + bg + fonts per theme)
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
