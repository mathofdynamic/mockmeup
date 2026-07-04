#!/usr/bin/env python3
"""
capture_app.py — Capture screenshots of a *running* web app with Playwright.

Used by /mockmeup mode (b): the project is runnable, so the skill starts the dev
server (or serves static HTML), then calls this to grab clean screenshots into the
project's screenshots/ folder.

It captures both a desktop viewport and (optionally) a mobile viewport so the poster
can choose phone vs browser framing. It auto-hides scrollbars and waits for fonts.

Usage:
    python capture_app.py http://localhost:5173 --out <project>/screenshots
        [--route / --route /pricing --route /#/map]   # extra paths/hashes
        [--name overview]                              # base filename for the root shot
        [--mobile]                                     # also grab 390x844 phone shots
        [--full]                                       # full-page (default: viewport only)
        [--wait 1800]                                  # settle ms after networkidle

Emits JSON: {"ok": true, "shots": [{"path","url","viewport","width","height"}], "errors":[...]}
"""
import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

CHROME_CANDIDATES = [
    r"C:\Users\matho\AppData\Local\ms-playwright\chromium-1187\chrome-win\chrome.exe",
    r"C:\Users\matho\AppData\Local\ms-playwright\chromium-1181\chrome-win\chrome.exe",
]
HIDE_SCROLLBAR = "*::-webkit-scrollbar{width:0!important;height:0!important;background:transparent!important}"


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    return ""


def join_route(base, route):
    # Support hash routes (#/x) and path routes (/x) and absolute urls.
    if route.startswith("http"):
        return route
    if route.startswith("#"):
        return base.rstrip("/") + "/" + route
    return urljoin(base if base.endswith("/") else base + "/", route.lstrip("/"))


def slug(route):
    s = route.strip("/#").replace("/", "-").replace("#", "").strip("-")
    return s or "home"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="base URL of the running app, e.g. http://localhost:5173")
    ap.add_argument("--out", required=True, help="output screenshots directory")
    ap.add_argument("--route", action="append", default=[], help="extra route/hash to capture (repeatable)")
    ap.add_argument("--name", default="overview", help="filename stem for the root/base shot")
    ap.add_argument("--mobile", action="store_true", help="also capture a 390x844 phone viewport")
    ap.add_argument("--full", action="store_true", help="full-page screenshots (default: viewport)")
    ap.add_argument("--wait", type=int, default=1800, help="ms to settle after networkidle")
    ap.add_argument("--desktop-size", default="1440x900", help="desktop viewport WxH")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    dw, dh = (int(x) for x in args.desktop_size.lower().split("x"))
    routes = args.route or ["/"]

    from playwright.sync_api import sync_playwright

    chrome = find_chrome()
    launch_kwargs = {"headless": True, "args": ["--no-sandbox", "--hide-scrollbars", "--force-color-profile=srgb"]}
    if chrome:
        launch_kwargs["executable_path"] = chrome

    shots = []
    errors = []

    viewports = [("desktop", dw, dh, 2)]
    if args.mobile:
        viewports.append(("mobile", 390, 844, 3))

    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_kwargs)
        try:
            for vp_name, vw, vh, scale in viewports:
                ctx = browser.new_context(viewport={"width": vw, "height": vh},
                                          device_scale_factor=scale)
                for route in routes:
                    url = join_route(args.url, route)
                    page = ctx.new_page()
                    page.on("pageerror", lambda e, r=route: errors.append(f"[{r}] {e}"))
                    try:
                        page.goto(url, wait_until="networkidle", timeout=40000)
                    except Exception as e:
                        errors.append(f"[{route}] goto: {e}")
                    try:
                        page.add_style_tag(content=HIDE_SCROLLBAR)
                        page.evaluate("document.fonts && document.fonts.ready")
                    except Exception:
                        pass
                    page.wait_for_timeout(args.wait)
                    stem = args.name if route in ("/", "") else slug(route)
                    fname = f"{stem}-{vp_name}.png" if len(viewports) > 1 else f"{stem}.png"
                    out_path = out_dir / fname
                    try:
                        page.screenshot(path=str(out_path), full_page=args.full)
                        shots.append({
                            "path": str(out_path).replace("\\", "/"),
                            "url": url,
                            "viewport": vp_name,
                            "width": vw, "height": vh, "scale": scale,
                        })
                    except Exception as e:
                        errors.append(f"[{route}] screenshot: {e}")
                    page.close()
                ctx.close()
        finally:
            browser.close()

    print(json.dumps({"ok": bool(shots), "shots": shots, "errors": errors}, indent=2, ensure_ascii=False))
    sys.exit(0 if shots else 3)


if __name__ == "__main__":
    main()
