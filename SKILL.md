---
name: mockmeup
description: >-
  Turn any app or project into a premium showcase mockup / poster image — a great background,
  the app's screenshots in nice device frames, and the app name + slogan. Use when the user says
  "/mockmeup", "make a mockup", "showcase this app", "make a poster/promo/hero image for this
  project", "I need a screenshot to show off my app", or wants a README hero / Product Hunt / social
  image. It uses an existing Screenshots folder if present; otherwise runs the app and captures shots
  itself; and if the project can't run (e.g. it's a skill, library, or CLI) it synthesizes a
  conceptual mockup from the project's info.
license: MIT
version: 0.1.0
---

# mockmeup — premium app showcase mockups

Produce a **premium poster image** that showcases a project: an atmospheric background, the app's
screenshots wrapped in device frames arranged in a good order, and typographic text (app name +
slogan + a few feature chips). Output is a crisp PNG the user can drop on a README, Product Hunt,
landing page, or social feed.

The end result must feel **designed and expensive** — not a flat gradient with Inter. Commit to one
bold aesthetic direction that matches the app's own brand.

## Setup: resolve MOCKMEUP_HOME (do this first)

The skill directory is **not** the working directory. Set `MOCKMEUP_HOME` to the absolute path of the
folder containing this SKILL.md, and prefix every `scripts/…`, `references/…`, `assets/…` path with
it. On this machine that is:

```
C:\Users\matho\.claude\skills\mockmeup
```

Determine the **target project**: the path the user gave, else the current working directory. Call it
`TARGET`. Decide the **output sizes** (default `social` + `og`; the user may ask for square/hero/story).

**Windows / shell note:** these Python scripts print UTF-8 and take URL/route args. When invoking via
the Bash tool, prefix commands with `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL="*" PYTHONUTF8=1` so Git
Bash does not mangle `/route` and `#/hash` arguments into Windows paths. (PowerShell doesn't need this.)

## Step 1 — Detect the project

```
python "$MOCKMEUP_HOME/scripts/detect_project.py" "TARGET"
```

Returns JSON with: `name`, `tagline`, `description`, `features[]`, `type`
(web/mobile/desktop/cli/library/skill/static/unknown), `runnable`, `run` (command + url_hint + kind),
`screenshots_dir`, `screenshots[]`, `logo`, `fonts[]` (bundled font files), `rtl` (bool) + `script`,
`primary_color`, `languages`, `signals`.

If `rtl` is true (or `fonts[]` lists a Persian/Arabic font), follow the RTL rules below — write copy in
the app's language, mirror the layout, and `@font-face` a `fonts[]` entry.

Use this to (a) choose the screenshot-source branch below, and (b) gather the **copy** (name, slogan,
chips) and **brand** (`primary_color`, logo) for the poster. Clean the name (drop repo-slug/hash
artifacts). If `tagline` is missing, write a crisp, specific 4–10 word value proposition from the
README/features — never a generic slogan, never invent features the project lacks.

**Language / RTL — check this every time.** Look at the README/UI text and the project's own screenshots.
If the app is Persian/Arabic/Hebrew/Urdu (or any RTL script), or otherwise non-English, the poster copy
**must be written in that language** and the layout must be RTL:
- Set `direction:rtl` on `.poster` (or the text container) and right-align text; the visual flow mirrors
  (text column on the **right**, screenshots bleeding off the **left**; for the og/wide split, text-right
  / screenshot-left).
- Keep browser chrome (traffic-light dots + URL) `direction:ltr` — URLs stay LTR even in an RTL poster.
- **Use the app's own font if it ships one.** If detect found a bundled font (e.g. a `.ttf`/`.woff` in
  the project, or a `@font-face` in its CSS), copy it next to the poster HTML and `@font-face` it — a
  matching Persian/Arabic font is a huge part of looking on-brand. Otherwise pick a quality webfont for
  that script (e.g. Vazirmatn/IRANSans-style for Persian) — never render RTL text in a Latin-only font.
- Write real, idiomatic copy in the language (name, tagline, chips) — don't transliterate or leave English.

## Step 2 — Get screenshots (pick ONE branch)

### Branch A — a Screenshots folder already exists (`screenshots_dir` is set)
Use the images in `screenshots[]`. Validate and order them:
```
python "$MOCKMEUP_HOME/scripts/check_screenshots.py" --dir "TARGET/<screenshots_dir>"
```
Keep the `usable` ones. Order by importance (a hero/overview/first shot in front). Each image reports
`orientation_frame` (phone/browser/card) — use it in Step 3. If a shot is rejected as
`blank_or_flat`/`too_small`, drop it and, if the app is also runnable, consider recapturing (Branch B).

### Branch B — no folder, but `runnable` is true
Start the app, capture it yourself, verify, and save into `TARGET/screenshots/`.

1. **Launch** per `run.command` in the project dir, in the **background**. For `kind: "static-html"`
   with no command, serve the folder: `python -m http.server 8899` from the static root (or `dist/`
   if a build exists) and use `http://localhost:8899`. For node dev servers use the `run.url_hint`
   (e.g. vite → :5173, next/CRA → :3000). Give it a few seconds; confirm it responds
   (`curl -s -o /dev/null -w "%{http_code}" <url>` → 200) before capturing.
2. **Capture:**
   ```
   python "$MOCKMEUP_HOME/scripts/capture_app.py" "<url>" --out "TARGET/screenshots" \
       --route "/" [--route "#/other" ...] [--mobile] --wait 1800
   ```
   Add `--mobile` for mobile-first apps (also grabs a 390×844 phone shot). Add extra `--route`s for a
   multi-screen app (inspect the router/nav to find good routes).
3. **Verify:** run `check_screenshots.py --dir "TARGET/screenshots"`. If shots are blank, increase
   `--wait`, wait for a specific selector, pick a different route, or try headed capture. Re-capture
   until you have usable shots.
4. **Always stop the dev server / http.server** when done.
5. The screenshots now live in `TARGET/screenshots/` (so next time Branch A applies).

### Branch C — not runnable (skill, library, CLI, empty, `type` in {skill,library,cli,unknown})
There's no live UI, so **synthesize** the visual instead of a real screenshot. Build the poster around:
- a **terminal window** showing representative commands/output (see `references/frames.md`), and/or
- **feature-highlight cards** built from `features[]`, and/or
- the **logo** as a hero mark, and/or a **code snippet** panel from a key source file, and/or
- generated **key art** (big typographic mark + the aurora/mesh background).

Pick what fits the project type (a CLI → terminal; a library/API → code panel; a skill → logo + feature
cards + terminal). No `screenshots/` folder is created in this branch.

## Step 3 — Design the poster

Read the three references and commit to ONE aesthetic:
- `references/backgrounds.md` — pick a premium background family; tune `--accent`/`--accent-2` to the
  app's `primary_color` (or its logo). **Always add grain + vignette.**
- `references/frames.md` — wrap each screenshot in the frame matching its `orientation_frame`; arrange
  multiple shots with depth/overlap in a good order.
- `references/layout.md` — choose the composition for the target size, the type scale, and the
  anti-slop checklist. Use distinctive fonts (Google Fonts `<link>` works at render time) — never
  default Inter/Roboto/Arial.

Build the poster HTML. Two options:
- **Fast path:** copy `assets/poster_template.html` and replace its `{{TOKENS}}`
  (`{{NAME}}` with one word wrapped in `<span class="hl">`, `{{TAGLINE}}`, `{{CHIP_1..3}}`, `{{SHOT_1}}`,
  `{{EYEBROW}}`, `{{URL}}`, `{{INITIAL}}` or swap the lettermark for `<img class="logo" src="{{LOGO}}">`).
  Adjust the background family + accent to fit.
- **Bespoke path (preferred for a standout result):** author fresh HTML for the chosen concept and
  size using the references. The template is a scaffold, not a ceiling.

Requirements for the HTML: a single `.poster` root sized via `width:var(--canvas-w)` /
`height:var(--canvas-h)`; screenshot/asset `src`s relative to the HTML file's location (copy chosen
screenshots next to the HTML, or use absolute paths). Write the HTML into `TARGET/mockups/` (create it).

If the frontend-design skill is available, lean on its aesthetic guidance while authoring.

## Step 4 — Render to PNG

```
python "$MOCKMEUP_HOME/scripts/render_poster.py" "TARGET/mockups/poster.html" \
    --out "TARGET/mockups" --size social --size og --scale 2
```
Sizes: `social` (1080×1350), `og`/`wide` (1200×630), `square` (1080×1080), `hero` (1920×1080),
`story` (1080×1920), or `WxH`. Output is retina (`--scale 2`) PNGs in `TARGET/mockups/`.

If the chosen size is landscape (og/hero) and the HTML was built for portrait, author a size-specific
layout (split text-left / screenshot-right per `layout.md`) rather than stretching the portrait one.

## Step 5 — Review and report

**Look at the rendered PNG** (Read the image). Check against the `layout.md` anti-slop checklist:
distinctive fonts, grain+vignette present, accent matches the app, framed screenshot with real shadow
and a slight angle/offset, one clear focal point, margins respected, tagline specific. If it looks
flat, generic, crowded, or off-brand, revise the HTML and re-render — don't ship the first draft if it
isn't premium.

**Balance the composition** (the most common first-draft flaw): scan for a large empty corner opposite
the text while the screenshots crowd/cut off the bottom edge. If you see that, fix it:
- Anchor the open corner with a faint element — a **ghosted brand-logo watermark** (~5–8% opacity,
  large, softly masked) and/or a soft accent glow — so the space reads as intentional, not empty.
- **Don't bleed a screenshot off more than one edge.** A shot cut on both the side and the bottom stops
  reading as a screen and becomes texture. Lift it so it sits fully in frame with a little breathing
  room, and keep only one edge bleeding (for depth).
- Group small meta labels (e.g. "100% Persian / RTL", version, platform) **into the chips row**, not
  floating alone in a corner.
- Aim for one clear focal read and deliberate negative space — not a dead-centered, evenly-filled grid.

Then report the saved file path(s) and offer variations (different aesthetic direction, background
family, size, or an alternate screenshot arrangement).

## Guardrails
- Never invent features/claims the project doesn't have; prefer the app's own words.
- Never upscale a tiny screenshot — recapture at higher resolution instead.
- Always stop any dev server / http.server you start.
- Match the poster's mood to the actual product (fintech ≠ kids' game).
- The bar is "would this look at home on a top-tier product's landing page?" If not, iterate.
