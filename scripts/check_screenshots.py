#!/usr/bin/env python3
"""
check_screenshots.py — Validate screenshots so /mockmeup never composites a blank or
broken shot into a premium poster.

For each image it reports:
  - dimensions + aspect ("portrait" | "landscape" | "square")
  - "orientation_frame": suggested frame ("phone" for tall, "browser" for wide)
  - is_blank: near-single-color (nothing rendered / white/black screen)
  - is_low_variance: very little visual content (probably an error/empty page)
  - too_small: below a usable resolution
  - verdict: "ok" | "reject"  (+ reasons)

Usage:
    python check_screenshots.py <img1> <img2> ...
    python check_screenshots.py --dir <folder>        # all images in a folder

Emits JSON: {"ok": true, "images":[...], "usable":[paths], "rejected":[paths]}
Exit 0 if at least one usable image; else 4.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from PIL import Image, ImageStat  # noqa: E402

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
MIN_W, MIN_H = 320, 320          # below this a shot is too small to look premium
BLANK_STDDEV = 3.5               # per-channel stddev under this ≈ flat color
LOWVAR_STDDEV = 8.0              # under this ≈ almost nothing rendered


def analyze(path: Path):
    info = {"path": str(path).replace("\\", "/"), "reasons": []}
    try:
        im = Image.open(path)
        im.load()
    except Exception as e:
        info.update({"verdict": "reject", "error": str(e)})
        info["reasons"].append("unreadable")
        return info

    w, h = im.size
    info["width"], info["height"] = w, h
    ratio = w / h if h else 0
    info["aspect"] = "square" if 0.9 <= ratio <= 1.1 else ("landscape" if ratio > 1.1 else "portrait")
    info["orientation_frame"] = "browser" if ratio > 1.15 else ("phone" if ratio < 0.85 else "card")

    rgb = im.convert("RGB")
    stat = ImageStat.Stat(rgb)
    mean_stddev = sum(stat.stddev) / len(stat.stddev)
    info["stddev"] = round(mean_stddev, 2)
    info["mean_rgb"] = [round(c) for c in stat.mean]

    too_small = w < MIN_W or h < MIN_H
    is_blank = mean_stddev < BLANK_STDDEV
    is_lowvar = mean_stddev < LOWVAR_STDDEV
    info["too_small"] = too_small
    info["is_blank"] = is_blank
    info["is_low_variance"] = is_lowvar and not is_blank

    if too_small:
        info["reasons"].append(f"too_small ({w}x{h})")
    if is_blank:
        info["reasons"].append("blank_or_flat")
    elif is_lowvar:
        info["reasons"].append("low_visual_content")

    info["verdict"] = "reject" if (too_small or is_blank) else "ok"
    if info["verdict"] == "ok" and is_lowvar:
        info["verdict"] = "ok"  # usable but flagged; skill can decide to recapture
        info["reasons"].append("warn:sparse")
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="*", help="image paths")
    ap.add_argument("--dir", help="a directory; validate every image inside")
    args = ap.parse_args()

    paths = [Path(p) for p in args.images]
    if args.dir:
        d = Path(args.dir)
        if d.is_dir():
            paths += sorted(p for p in d.iterdir()
                            if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
    if not paths:
        print(json.dumps({"ok": False, "error": "no images given"}))
        sys.exit(4)

    results = [analyze(p) for p in paths]
    usable = [r["path"] for r in results if r["verdict"] == "ok"]
    rejected = [r["path"] for r in results if r["verdict"] == "reject"]

    print(json.dumps({
        "ok": bool(usable),
        "usable": usable,
        "rejected": rejected,
        "images": results,
    }, indent=2, ensure_ascii=False))
    sys.exit(0 if usable else 4)


if __name__ == "__main__":
    main()
