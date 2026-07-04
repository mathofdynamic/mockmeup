# Device frames & screenshot presentation

How to wrap a raw screenshot so it looks intentional and premium. **Auto-pick the frame
from the screenshot's aspect** (check_screenshots.py reports `orientation_frame`):

| Screenshot shape | Frame | When |
|---|---|---|
| portrait (h > w) | **phone** | mobile app / mobile web capture |
| landscape (w > h) | **browser window** | web app / dashboard |
| landscape, code/terminal content | **terminal** | CLI / dev tool |
| any | **floating card** | fallback; clean and universal |

Common polish for every frame: big soft shadow, slight rounding, optional 1px light inner
border, and a subtle tilt/scale for energy. Keep screenshots pixel-crisp (`image-rendering`
default; never upscale a tiny shot — recapture instead).

Shared shadow + reflection helpers:
```css
.shadow-xl{ box-shadow:0 40px 80px -20px rgba(0,0,0,.55), 0 12px 30px -10px rgba(0,0,0,.4); }
.edge{ box-shadow:inset 0 0 0 1px rgba(255,255,255,.08); }
.tilt{ transform:perspective(1600px) rotateY(-9deg) rotateX(3deg); } /* hero angle */
.reflection{ /* optional floor reflection */
  -webkit-box-reflect:below 8px linear-gradient(transparent 70%, rgba(255,255,255,.12));
}
```

---

## Browser window (macOS-style) — for web apps / dashboards
```html
<div class="browser shadow-xl edge">
  <div class="chrome">
    <span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
    <div class="url">appname.com</div>
  </div>
  <img class="shot" src="SCREENSHOT.png" alt="">
</div>
```
```css
.browser{ border-radius:14px; overflow:hidden; background:#12131a; width:min(92%, 1100px); }
.chrome{ display:flex; align-items:center; gap:8px; padding:12px 16px;
         background:linear-gradient(#20222c,#181a22); }
.dot{ width:12px; height:12px; border-radius:50%; }
.dot.r{background:#ff5f57} .dot.y{background:#febc2e} .dot.g{background:#28c840}
.url{ margin-left:14px; flex:1; max-width:60%; height:26px; border-radius:8px;
      background:#0d0e14; color:#8b90a3; font:13px/26px ui-monospace,monospace;
      padding:0 12px; }
.browser .shot{ display:block; width:100%; }
```

## Phone frame — for mobile apps / portrait captures
Pure-CSS device; no asset needed.
```html
<div class="phone shadow-xl"><div class="notch"></div><img class="shot" src="SCREENSHOT.png"></div>
```
```css
.phone{ position:relative; width:340px; padding:14px; border-radius:52px;
        background:linear-gradient(160deg,#2a2c34,#111318); }
.phone::after{ content:""; position:absolute; inset:6px; border-radius:46px;
               box-shadow:inset 0 0 0 2px rgba(255,255,255,.06); pointer-events:none; }
.notch{ position:absolute; top:22px; left:50%; transform:translateX(-50%);
        width:120px; height:26px; background:#000; border-radius:14px; z-index:2; }
.phone .shot{ display:block; width:100%; border-radius:40px; }
```

## Laptop frame — for wide desktop hero shots
```html
<div class="laptop"><div class="screen"><img class="shot" src="SCREENSHOT.png"></div><div class="base"></div></div>
```
```css
.laptop{ width:min(90%,1000px); }
.laptop .screen{ background:#0c0d12; border:10px solid #1c1e26; border-radius:16px 16px 0 0;
                 overflow:hidden; box-shadow:0 30px 60px -20px rgba(0,0,0,.6); }
.laptop .shot{ display:block; width:100%; }
.laptop .base{ height:20px; border-radius:0 0 14px 14px;
               background:linear-gradient(#c9ccd6,#8b8f9c); position:relative; }
.laptop .base::after{ content:""; position:absolute; top:0; left:50%; transform:translateX(-50%);
                      width:120px; height:8px; border-radius:0 0 10px 10px; background:#5f6270; }
```

## Terminal window — for CLI / dev tools / "not runnable" code visuals
Great for mode (c) when there's no screenshot: render code/output as styled terminal text.
```html
<div class="term shadow-xl edge">
  <div class="chrome"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
    <span class="title">zsh — appname</span></div>
  <pre class="body"><span class="p">$</span> appname build
<span class="ok">✓</span> compiled in 240ms
<span class="p">$</span> <span class="cur">▋</span></pre>
</div>
```
```css
.term{ width:min(92%,900px); border-radius:12px; overflow:hidden; background:#0d1017; }
.term .chrome{ background:#171b24; padding:10px 14px; display:flex; align-items:center; gap:8px; }
.term .title{ margin-left:12px; color:#7c8394; font:12px ui-monospace,monospace; }
.term .body{ margin:0; padding:22px 24px; color:#d6dbe7;
             font:15px/1.7 ui-monospace,"Cascadia Code",monospace; }
.term .p{ color:var(--accent); } .term .ok{ color:#39d98a; }
.term .cur{ animation:blink 1s steps(1) infinite; }
@keyframes blink{ 50%{opacity:0} }
```

## Floating card — universal fallback
No chrome, just a beautifully-shadowed rounded screenshot.
```css
.card-shot{ border-radius:18px; overflow:hidden; width:min(90%,1000px);
            box-shadow:0 50px 90px -30px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.06); }
.card-shot img{ display:block; width:100%; }
```

---

## Arranging multiple screenshots — the ≥55% visibility rule (READ THIS)

**Hard rule: every screenshot you place must stay at least ~55% visible.** A shot that ends up mostly
hidden behind another is worse than not including it — it reads as clutter, not a screen. This is the
single most common failure (a whole second screenshot buried behind the first). If two shots can't both
be ≥55% visible in the arrangement you're trying, either switch to a side-by-side/cascade arrangement,
shrink the hero, or **drop the extra shot**. Fewer, fully-readable screens > more, buried ones.

Pick an arrangement where each frame is clearly its own screen:

- **1 shot** → hero it: large, centered or angled with `.tilt`, generous margin. (Always fine.)
- **2 shots — staggered duo (preferred):** offset them mostly *sideways*, not stacked. The back shot
  sits up-and-behind by ~18–22% and is dimmed (`filter:brightness(.82)`); the front shot overlaps it by
  **no more than ~40%** so ~60% of the back shot still shows. Both remain identifiable.
  ```css
  .duo{ position:relative; }
  .duo .back{ position:absolute; top:0; left:34%; width:66%; filter:brightness(.82); transform:rotate(2deg); }
  .duo .front{ position:relative; width:70%; z-index:2; } /* overlaps back by ~40%, back stays ~60% visible */
  ```
- **2 shots — split pane:** two frames side by side, a small gap, slight opposite tilts. Zero occlusion;
  safest when both screens matter equally.
- **3 shots — diagonal cascade:** step them down-and-across so each lower shot reveals the one above by
  ≥55%; front sharp, ones behind progressively dimmed. Order by importance (hero first/front).
- **hero + detail card:** one large browser/laptop shot + one small *fully-visible* floating card (a
  cropped detail, a phone, a stat) tucked in a corner with its own shadow — never overlapping the hero's
  focal content.
- **phone set** → line up 2–3 phones with slight vertical offset and rotation (`-4deg`, `0deg`, `4deg`),
  overlapping ≤35% so each screen face is readable.

Common polish: keep 40–80px gaps, let frame shadows breathe against the background, and **bleed a shot off
at most ONE edge** (a shot cut on two edges stops reading as a screen). Leave a clear margin — composed,
not stuffed.
