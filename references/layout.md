# Poster layout & typography

The rules that make the composition feel *designed*, not auto-generated. Read
`backgrounds.md` (atmosphere) and `frames.md` (screenshot presentation) alongside this.

## The canvas
`render_poster.py` injects `--canvas-w` / `--canvas-h` and screenshots the `.poster`
element. Your root must be:
```css
.poster{ width:var(--canvas-w,1080px); height:var(--canvas-h,1350px);
         position:relative; overflow:hidden; }
```
Design for the **default size the skill is rendering** — don't try to make one layout
serve every ratio equally. Pick the composition per ratio:

| Size | Ratio | Composition |
|---|---|---|
| social 1080×1350 | 4:5 portrait | Text block top (name + tagline + chips), screenshot(s) fill lower 60–65%. Or center hero with text above. |
| og / wide 1200×630 | ~1.9:1 | **Split**: text on the left ~42%, framed screenshot on the right (angled/bleeding off the edge). |
| square 1080×1080 | 1:1 | Centered: logo + name top, one hero screenshot below, tagline under it. |
| hero 1920×1080 | 16:9 | Big left text, large laptop/browser shot right, generous negative space. |
| story 1080×1920 | 9:16 | Vertical stack: name top third, tall phone frame center, tagline/chips bottom. |

## Typographic system (pick fonts with character — NOT Inter/Roboto/Arial)
Load Google Fonts via `<link>` in `<head>` (network is available at render time), OR use a
strong system stack. Pair a **display** face (headline) with a **body** face (tagline/chips).

Good pairings by aesthetic:
- Refined/tech: `Space Grotesk`/`Sora` display + `Inter Tight`/`IBM Plex Sans` body. *(avoid plain Inter)*
- Editorial/premium: `Fraunces` or `Instrument Serif` display + `Newsreader`/`Source Serif` body.
- Bold/consumer: `Clash Display`/`Bricolage Grotesque` display + `Satoshi`/`General Sans` body.
- Luxury: `Cormorant Garamond`/`Playfair Display` display + thin sans body.
- Dev/mono accent: headline sans + `JetBrains Mono`/`Cascadia Code` for chips/labels.

Vary across generations — do not always reach for the same font.

Scale (for a 1080-wide canvas; scale proportionally for others):
```
app name (display)   72–120px, weight 600–800, letter-spacing -1 to -3px, line-height .95–1.05
tagline (body)       30–40px, weight 400–500, opacity .82, max-width ~22 chars/line ×2–3 lines
eyebrow/kicker        16–20px, uppercase, letter-spacing 3–5px, accent color
feature chips         18–24px, in pill: padding 10px 18px, border-radius 999px,
                       bg color-mix(accent 14%, transparent), 1px accent-tinted border
logo mark            48–72px square
```

## Color & contrast
- Set `--accent` from the app's `primary_color` (detect_project) or eyedrop the logo. Derive
  `--accent-2` as an analogous/complementary hue.
- Highlight ONE word of the app name or tagline in `--accent` for a focal point.
- Ensure text passes contrast: light `--ink` on dark bg, dark `--ink` on light bg. If a
  screenshot sits behind text, add a scrim (`background:linear-gradient(transparent, rgba(0,0,0,.6))`).
- Restraint beats rainbow: dominant neutral + one accent reads more premium than many colors.

## Composition principles
- **One focal point.** The eye should land on the hero screenshot or the app name first.
- **Alignment grid.** Pick a margin (≈6–8% of width) and align text and frames to it.
- **Asymmetry & overlap** create energy — angle a frame, let it bleed off one edge, overlap
  a secondary shot behind the hero. Avoid a dead-centered, evenly-spaced "template" look.
- **Negative space** is premium. Don't fill every pixel; let the background breathe.
- **Depth stack** (back→front): background gradient → glow → grain/vignette → secondary
  screenshots (dimmed) → hero screenshot (sharp, shadowed) → text/logo on top.
- **Consistency** with the app: echo its actual UI accent color and mood (a fintech app ≠ a
  kids' game). The poster should feel like it belongs to that product.

## RTL & non-English apps
If the app is Persian/Arabic/Hebrew/Urdu (or any RTL/non-Latin product), the poster must match:
- Write all copy **in the app's language** (name, tagline, chips) — idiomatic, not transliterated.
- `direction:rtl` on the poster/text; right-align text. The whole composition **mirrors**: text column
  on the right, screenshots bleeding off the left; for og/wide, text-right / screenshot-left.
- Keep the browser frame's chrome `direction:ltr` (traffic-light dots + URL stay LTR).
- Use the app's **own bundled font** if it has one (copy the `.ttf`/`.woff` next to the HTML and
  `@font-face` it) — this is the single biggest on-brand win. Otherwise pick a real font for that
  script (Persian → Vazirmatn/IRANSans-style); never render RTL text in a Latin-only face.
- Persian/Arabic digits and punctuation should match the app (e.g. ۱۰۰٪, not 100%).

## Balance & negative space (avoid the #1 first-draft flaw)
A common failure: the text sits in one corner, the opposite corner is a big empty wash, and the
screenshots crowd/cut off the bottom. Fix by:
- **Anchor the open corner** with a faint element: a ghosted brand-logo watermark (~5–8% opacity, large,
  softly masked with a radial `mask-image`) and/or a soft accent glow. Empty space should feel chosen.
- **One bleeding edge per screenshot.** A shot cut on both a side and the bottom reads as texture, not a
  screen. Lift shots fully into frame with a little bottom breathing room; let only one edge run off.
- **Group meta labels into the chips row** (locale/version/platform pills) rather than floating them alone.
- Keep a clear focal read; don't fill every pixel evenly.

## Copy (text content)
- **App name**: from detect_project `name` (clean it — drop repo-slug artifacts).
- **Tagline/slogan**: use the detected `tagline`; if missing, write a crisp 4–8 word value
  proposition from the README/features. Confident, specific, not generic ("Ship faster" < "The
  competitive-intelligence dashboard for AI products").
- **Chips**: 2–4 short feature highlights or a tech-stack row. Keep each ≤3 words.
- Never invent features the project doesn't have. Prefer the app's own words.

## Anti-slop checklist (before rendering)
- [ ] Distinctive fonts (not Inter/Roboto/Arial default).
- [ ] Background has grain + vignette, not a flat gradient.
- [ ] Accent color matches the actual app.
- [ ] Screenshot is in a frame with a real shadow, slightly angled or offset.
- [ ] One clear focal point; margins respected; not center-locked & evenly spaced.
- [ ] Tagline is specific to this product, not a generic slogan.
- [ ] No large empty corner opposite the text; open space is anchored (watermark/glow) & intentional.
- [ ] No screenshot bleeding off two edges; shots sit fully in frame with breathing room.
- [ ] RTL/non-English app → copy in the app's language, mirrored layout, correct script font.
