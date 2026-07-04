# Premium background recipes

Copy-paste CSS backgrounds that read as premium marketing art (Stripe / Linear / Vercel /
Apple energy). All are pure CSS — offline, deterministic, no images. Apply to the
`.bg` layer behind the content. **Pick ONE family per poster and commit to it**, then tune
the accent hue to the app's brand color (`--accent`).

Layering rule for depth: **base gradient → 1–3 glow blobs → texture (grain/dots) → vignette**.
Always finish with the grain + vignette overlays (bottom of this file) — that single step is
what separates "premium" from "flat CSS gradient".

Set these vars near `:root` and reference them:
```css
:root{
  --accent:#5b8cff;         /* app brand color; sniff from manifest/css or pick to match logo */
  --accent-2:#c874ff;       /* secondary; analogous or complementary */
  --ink:#f5f7ff;            /* foreground text on dark bg */
  --bg-0:#080b16;           /* deepest background */
}
```

---

## 1. Aurora / spotlight mesh (dark, default — safest premium look)
Soft off-center colored glows over near-black. Works for almost any app.
```css
.bg{
  background:
    radial-gradient(60% 50% at 18% 12%, color-mix(in oklab, var(--accent) 55%, transparent) 0%, transparent 60%),
    radial-gradient(55% 55% at 88% 82%, color-mix(in oklab, var(--accent-2) 50%, transparent) 0%, transparent 55%),
    radial-gradient(80% 60% at 50% 120%, color-mix(in oklab, var(--accent) 22%, transparent) 0%, transparent 60%),
    linear-gradient(160deg, #0a0e1c 0%, var(--bg-0) 60%, #05070f 100%);
}
```

## 2. Editorial light (premium on white — for clean/productivity apps)
Warm paper white with one restrained accent wash. Great with dark screenshots.
```css
.bg{
  background:
    radial-gradient(70% 60% at 85% 0%, color-mix(in oklab, var(--accent) 18%, transparent), transparent 60%),
    radial-gradient(50% 50% at 0% 100%, color-mix(in oklab, var(--accent-2) 12%, transparent), transparent 55%),
    linear-gradient(180deg, #fbfbfd, #f2f2f7);
  --ink:#0d1220; /* switch text to dark on this bg */
}
```

## 3. Mesh gradient (colorful, confident — for creative/consumer apps)
Overlapping saturated blobs. Bolder; keep text in a high-contrast panel.
```css
.bg{
  background:
    radial-gradient(40% 40% at 20% 25%, #ff8fb1 0%, transparent 55%),
    radial-gradient(45% 45% at 78% 20%, #7c5cff 0%, transparent 55%),
    radial-gradient(50% 50% at 70% 85%, #38e0c8 0%, transparent 55%),
    radial-gradient(40% 40% at 15% 80%, #ffd16b 0%, transparent 55%),
    #0e0b1a;
  filter:saturate(1.05);
}
```

## 4. Deep gradient + grid (technical / developer tools)
Diagonal deep gradient with a faint engineering grid. Signals "serious tool".
```css
.bg{
  background:
    linear-gradient(135deg, #0b1220 0%, #0f1830 55%, #0a0f1f 100%);
}
.bg::before{ /* the grid */
  content:""; position:absolute; inset:0;
  background-image:
    linear-gradient(color-mix(in oklab, var(--accent) 18%, transparent) 1px, transparent 1px),
    linear-gradient(90deg, color-mix(in oklab, var(--accent) 18%, transparent) 1px, transparent 1px);
  background-size:48px 48px;
  mask-image:radial-gradient(80% 70% at 50% 30%, #000 0%, transparent 75%);
  opacity:.5;
}
```

## 5. Luxury dark + gold (premium/finance/pro)
Near-black with a single warm metallic sweep. Restrained and expensive-looking.
```css
.bg{
  background:
    radial-gradient(60% 50% at 80% 10%, rgba(212,175,110,.28), transparent 55%),
    conic-gradient(from 210deg at 20% 90%, rgba(212,175,110,.14), transparent 40%),
    linear-gradient(160deg, #0c0c0e, #141416 60%, #0a0a0c);
  --accent:#d4af6e; --accent-2:#b98a3e;
}
```

## 6. Soft pastel dusk (friendly / lifestyle / mobile apps)
Gentle vertical dusk gradient; pairs beautifully with a phone frame.
```css
.bg{
  background:
    radial-gradient(60% 40% at 50% 0%, #ffd9a8 0%, transparent 55%),
    linear-gradient(180deg, #ffb3c9 0%, #b48cff 45%, #6a5cff 100%);
  --ink:#1a1030;
}
```

---

## Texture + vignette overlays (ALWAYS add these last)
Put these as extra absolutely-positioned layers inside `.bg`.

**Film grain** (SVG noise as a data-URI — no external file):
```css
.grain{
  position:absolute; inset:0; pointer-events:none; opacity:.06; mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
  background-size:180px 180px;
}
```

**Vignette** (focuses the eye, adds depth):
```css
.vignette{
  position:absolute; inset:0; pointer-events:none;
  box-shadow:inset 0 0 240px 40px rgba(0,0,0,.45);
}
```

**Dot matrix** (alternative to grid, subtle):
```css
.dots{
  position:absolute; inset:0; opacity:.4; pointer-events:none;
  background-image:radial-gradient(color-mix(in oklab, var(--ink) 30%, transparent) 1px, transparent 1.4px);
  background-size:22px 22px;
  mask-image:radial-gradient(70% 60% at 50% 40%, #000, transparent 80%);
}
```

## Choosing which family
- Unknown / SaaS / "make it look pro" → **#1 Aurora** (dark) or **#2 Editorial** (light).
- Colorful consumer / creative → **#3 Mesh**.
- Dev tool / CLI / API → **#4 Grid**.
- Finance / premium / "luxury" → **#5 Gold**.
- Mobile / lifestyle / playful → **#6 Pastel**.
- Match `--accent`/`--accent-2` to the app's `primary_color` (from detect_project) or its logo.
- Never ship the cliché: flat purple gradient on white with Inter. Add grain + vignette every time.
