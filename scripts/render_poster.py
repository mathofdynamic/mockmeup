#!/usr/bin/env python3
"""
render_poster.py — Render a fixed-canvas HTML poster to crisp PNG(s) via Playwright.

This is the load-bearing output step of the /mockmeup skill. It loads a local HTML
file (the poster) in headless Chromium and screenshots a single fixed-size element
(the ".poster" node, or <body> if absent) at retina scale.

Why Playwright + on-disk Chromium: `playwright install` downloads fail on this
machine, so we point `executablePath` at the Chromium that is already present.

Usage:
    python render_poster.py poster.html --out ./mockups \
        --size 1080x1350 --size 1200x630 --scale 2

    # size can also be a named preset:
    python render_poster.py poster.html --size social --size og

Each --size produces <stem>-<WxH>.png in --out (default: alongside the html).
The HTML is expected to read CSS custom properties --canvas-w / --canvas-h so the
same template can render at any requested size; render_poster injects them before
the shot, and also sets the viewport to match. If the HTML pins its own size, that
still works — we screenshot the .poster element's real box.

Exit code 0 on success; non-zero (with a JSON error on stdout) on failure.
"""
import argparse
import json
import os
import sys
from pathlib import Path

CHROME_CANDIDATES = [
    r"C:\Users\matho\AppData\Local\ms-playwright\chromium-1187\chrome-win\chrome.exe",
    r"C:\Users\matho\AppData\Local\ms-playwright\chromium-1181\chrome-win\chrome.exe",
]

# Named size presets (width, height) in CSS px.
PRESETS = {
    "social": (1080, 1350),   # 4:5 portrait — Instagram/LinkedIn/Twitter feed
    "og": (1200, 630),        # OpenGraph / README header / Product Hunt
    "wide": (1200, 630),
    "square": (1080, 1080),   # IG grid / app store
    "hero": (1920, 1080),     # 16:9 desktop hero / slide
    "story": (1080, 1920),    # 9:16 phone story
}


def find_chrome() -> str:
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    # Fall back to whatever Playwright bundles, if the pinned paths moved.
    return ""


def parse_size(token: str):
    token = token.strip().lower()
    if token in PRESETS:
        return PRESETS[token]
    if "x" in token:
        w, _, h = token.partition("x")
        return (int(w), int(h))
    raise ValueError(f"unrecognized size: {token!r} (use WxH or a preset name)")


def render(html_path: Path, out_dir: Path, sizes, scale: int):
    from playwright.sync_api import sync_playwright

    url = html_path.resolve().as_uri()
    chrome = find_chrome()
    results = []

    launch_kwargs = {"headless": True, "args": ["--no-sandbox", "--force-color-profile=srgb"]}
    if chrome:
        launch_kwargs["executable_path"] = chrome

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        try:
            for (w, h) in sizes:
                ctx = browser.new_context(
                    viewport={"width": w, "height": h},
                    device_scale_factor=scale,
                )
                page = ctx.new_page()
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.goto(url, wait_until="networkidle", timeout=45000)
                # Expose the requested canvas size to the poster's CSS so a
                # responsive template can lay itself out for this exact ratio.
                page.add_style_tag(content=f":root{{--canvas-w:{w}px;--canvas-h:{h}px;}}")
                # Let webfonts + CSS animations settle.
                try:
                    page.evaluate("document.fonts && document.fonts.ready")
                except Exception:
                    pass
                page.wait_for_timeout(900)

                target = page.query_selector(".poster") or page.query_selector("body")
                out_path = out_dir / f"{html_path.stem}-{w}x{h}.png"
                target.screenshot(path=str(out_path))
                results.append({
                    "size": f"{w}x{h}",
                    "path": str(out_path),
                    "scale": scale,
                    "page_errors": errors,
                })
                ctx.close()
        finally:
            browser.close()
    return results


def main():
    ap = argparse.ArgumentParser(description="Render an HTML poster to PNG via Playwright.")
    ap.add_argument("html", help="path to the poster .html file")
    ap.add_argument("--out", default=None, help="output directory (default: alongside the html)")
    ap.add_argument("--size", action="append", default=[],
                    help="WxH or preset (social/og/square/hero/story). Repeatable. "
                         "Default: social + og.")
    ap.add_argument("--scale", type=int, default=2, help="device scale factor (default 2 = retina)")
    args = ap.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(json.dumps({"ok": False, "error": f"html not found: {html_path}"}))
        sys.exit(1)

    out_dir = Path(args.out) if args.out else html_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    size_tokens = args.size or ["social", "og"]
    try:
        sizes = [parse_size(t) for t in size_tokens]
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)

    try:
        results = render(html_path, out_dir, sizes, args.scale)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}))
        sys.exit(2)

    print(json.dumps({"ok": True, "chrome": find_chrome() or "(bundled)", "outputs": results}, indent=2))


if __name__ == "__main__":
    main()
