#!/usr/bin/env python3
"""
detect_project.py — Inspect a project folder and report everything /mockmeup needs
to decide HOW to showcase it.

Emits a single JSON object to stdout:
{
  "path": "...",
  "name": "Better Preview",
  "tagline": "…",                # best-guess one-liner
  "description": "…",            # longer blurb if found
  "features": ["…", "…"],        # bullet-y highlights pulled from README
  "type": "web|mobile|desktop|cli|library|skill|static|unknown",
  "runnable": true/false,
  "run": { "command": "npm run dev", "url_hint": "http://localhost:5173", "kind": "node-dev" },
  "screenshots_dir": "screenshots" | null,   # existing folder (any case) if present
  "screenshots": ["screenshots/a.png", ...], # images already inside it
  "logo": "assets/logo.svg" | null,
  "primary_color": "#5b8cff" | null,         # sniffed from manifest/css if any
  "languages": {"Python": 12, "TypeScript": 3},
  "signals": ["package.json", "SKILL.md", ...]
}

Pure stdlib. Read-only. Never launches anything; it only *reports* how to run.
The skill (Claude) decides what to do with this.
"""
import json
import os
import re
import sys
from pathlib import Path

# Windows console defaults to cp1252; project text is often non-ASCII (emoji, RTL).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build",
             ".next", ".nuxt", "target", ".idea", ".vscode", "vendor", "coverage",
             ".mypy_cache", ".pytest_cache", "ms-playwright", "site-packages"}

LANG_BY_EXT = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".rs": "Rust", ".go": "Go", ".java": "Java", ".kt": "Kotlin",
    ".swift": "Swift", ".rb": "Ruby", ".php": "PHP", ".c": "C", ".cpp": "C++",
    ".cs": "C#", ".html": "HTML", ".css": "CSS", ".vue": "Vue", ".svelte": "Svelte",
    ".sh": "Shell", ".dart": "Dart",
}


def read_text(p: Path, limit=200_000):
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def load_json(p: Path):
    try:
        return json.loads(read_text(p))
    except Exception:
        return None


def walk(root: Path, max_files=6000):
    """Yield files, skipping heavy/vendor dirs, capped."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
                       or d in {".claude"}]
        for f in filenames:
            yield Path(dirpath) / f
            count += 1
            if count >= max_files:
                return


def find_screenshots_dir(root: Path):
    for child in root.iterdir() if root.exists() else []:
        if child.is_dir() and child.name.lower() in {"screenshots", "screenshot", "shots"}:
            return child
    return None


FONT_EXTS = {".ttf", ".otf", ".woff", ".woff2"}


def find_fonts(root: Path, limit=8):
    """Bundled font files — used to render on-brand (esp. RTL) text in the poster."""
    fonts = []
    for f in walk(root):
        if f.suffix.lower() in FONT_EXTS:
            try:
                fonts.append(str(f.relative_to(root)).replace("\\", "/"))
            except Exception:
                pass
        if len(fonts) >= limit:
            break
    return fonts


def detect_rtl(*texts):
    """True if the project's own text is meaningfully RTL (Arabic/Persian/Hebrew/…).

    Returns (rtl: bool, script: str|None). Uses a ratio so a stray character doesn't flip it.
    """
    rtl_chars = 0
    letters = 0
    script = None
    for t in texts:
        if not t:
            continue
        for ch in t:
            o = ord(ch)
            if ch.isalpha():
                letters += 1
            # Arabic (incl. Persian/Urdu), Hebrew, Syriac, Thaana
            if (0x0590 <= o <= 0x05FF) or (0x0600 <= o <= 0x06FF) or \
               (0x0700 <= o <= 0x074F) or (0x0750 <= o <= 0x077F) or \
               (0x0780 <= o <= 0x07BF) or (0xFB50 <= o <= 0xFDFF) or (0xFE70 <= o <= 0xFEFF):
                rtl_chars += 1
                if script is None:
                    script = "hebrew" if o <= 0x05FF else "arabic"
    ratio = rtl_chars / max(letters, 1)
    # RTL-dominant text (docs in the language), OR a substantial amount of RTL content at a
    # non-trivial ratio (an English-doc'd app whose UI/strings are clearly in an RTL script).
    # The dual test avoids false positives from tools that merely process foreign data.
    if letters and (ratio > 0.12 or (rtl_chars >= 800 and ratio >= 0.04)):
        return True, script
    return False, None


TEXTY_EXTS = {".md", ".txt", ".html", ".htm", ".json", ".vue", ".svelte",
              ".jsx", ".tsx", ".js", ".ts", ".css"}


def gather_text_sample(root: Path, max_files=14, per_file=16_000):
    """Concatenate a bounded sample of the project's own text so RTL detection sees the
    real UI language even when the README happens to be in English."""
    noisy = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock")
    chunks = []
    seen = 0
    for f in walk(root):
        if seen >= max_files:
            break
        n = f.name.lower()
        if f.suffix.lower() not in TEXTY_EXTS:
            continue
        if n in noisy or ".min." in n or n.endswith(".map") or "secret" in n:
            continue
        try:
            if f.stat().st_size > 2_000_000:  # skip huge bundles/minified files
                continue
        except Exception:
            continue
        chunks.append(read_text(f, limit=per_file))
        seen += 1
    return "\n".join(chunks)


def find_logo(root: Path):
    # Prefer explicit logo/icon names, shallowly.
    candidates = []
    patterns = ["logo", "icon", "appicon", "app-icon", "brand"]
    search_dirs = [root, root / "assets", root / "public", root / "static",
                   root / "src" / "assets", root / "images", root / "img", root / "docs"]
    for d in search_dirs:
        if not d.exists() or not d.is_dir():
            continue
        for child in d.iterdir():
            if child.is_file() and child.suffix.lower() in IMAGE_EXTS | {".svg"}:
                stem = child.stem.lower()
                if any(pat in stem for pat in patterns):
                    # rank: svg > png, "logo" > "icon"
                    score = (0 if child.suffix.lower() == ".svg" else 1,
                             0 if "logo" in stem else 1, len(stem))
                    candidates.append((score, child))
    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    # fallback: favicon
    for name in ["favicon.svg", "favicon.png", "favicon.ico"]:
        for d in [root, root / "public", root / "static"]:
            if (d / name).exists():
                return d / name
    return None


def extract_readme(root: Path):
    """Return (name, tagline, description, features) from the first README found."""
    readme = None
    for name in ["README.md", "readme.md", "Readme.md", "README.MD", "README.txt", "README"]:
        if (root / name).exists():
            readme = root / name
            break
    name = tagline = description = None
    features = []
    if readme:
        text = read_text(readme)
        lines = [l.rstrip() for l in text.splitlines()]
        # name = first H1
        for l in lines:
            m = re.match(r"^#\s+(.+)", l)
            if m:
                name = re.sub(r"[#*`_]", "", m.group(1)).strip()
                break
        # tagline = first substantial non-heading, non-badge line
        for l in lines:
            s = l.strip()
            if not s or s.startswith("#") or s.startswith("![") or s.startswith("[!["):
                continue
            if s.startswith("<") or s.startswith("---") or s.startswith("```"):
                continue
            s = re.sub(r"[*`_>]", "", s).strip()
            if len(s) > 12:
                tagline = s[:160]
                break
        description = tagline
        # features = bullet lines (first block of them)
        for l in lines:
            m = re.match(r"^\s*[-*+]\s+(.+)", l)
            if m:
                item = re.sub(r"[*`_\[\]]", "", m.group(1)).strip()
                item = re.sub(r"\(https?://[^)]+\)", "", item).strip()
                if 3 < len(item) < 120 and not item.lower().startswith("http"):
                    features.append(item)
            if len(features) >= 6:
                break
    return name, tagline, description, features


def sniff_color(root: Path):
    # manifest theme_color, or a --primary/--accent css var, or a hex in a small css
    for mp in ["manifest.json", "public/manifest.json", "src/manifest.json"]:
        data = load_json(root / mp)
        if isinstance(data, dict):
            for k in ("theme_color", "background_color"):
                v = data.get(k)
                if isinstance(v, str) and re.match(r"^#?[0-9a-fA-F]{3,8}$", v.strip()):
                    return v if v.startswith("#") else "#" + v
    for cssname in ["src/index.css", "src/App.css", "styles.css", "src/styles.css",
                    "app/globals.css", "src/app/globals.css"]:
        css = read_text(root / cssname, limit=40_000)
        if css:
            m = re.search(r"--(?:primary|accent|brand|main)[\w-]*\s*:\s*(#[0-9a-fA-F]{3,8})", css)
            if m:
                return m.group(1)
    return None


def classify(root: Path, signals: set):
    """Return (type, runnable, run_dict)."""
    pkg = load_json(root / "package.json")
    has_index_html = (root / "index.html").exists()

    # ---- Skill / plugin (a project that IS a claude skill) ----
    if (root / "SKILL.md").exists():
        return "skill", False, None

    # ---- Node / web ----
    if pkg:
        scripts = pkg.get("scripts", {}) if isinstance(pkg, dict) else {}
        deps = {}
        for key in ("dependencies", "devDependencies"):
            d = pkg.get(key) if isinstance(pkg, dict) else None
            if isinstance(d, dict):
                deps.update(d)
        dep_names = set(deps)

        # mobile
        if {"react-native", "expo"} & dep_names:
            return "mobile", False, None
        # desktop
        if {"electron", "@tauri-apps/api", "tauri"} & dep_names:
            cmd = "npm run dev" if "dev" in scripts else ("npm start" if "start" in scripts else None)
            return "desktop", bool(cmd), ({"command": cmd, "kind": "desktop", "url_hint": None} if cmd else None)
        # web dev server
        dev_cmd = None
        url_hint = None
        for cand in ("dev", "start", "serve", "preview"):
            if cand in scripts:
                dev_cmd = f"npm run {cand}"
                break
        # framework-based url hints
        if "vite" in dep_names:
            url_hint = "http://localhost:5173"
        elif "next" in dep_names:
            url_hint = "http://localhost:3000"
        elif {"react-scripts"} & dep_names:
            url_hint = "http://localhost:3000"
        elif {"@angular/core"} & dep_names:
            url_hint = "http://localhost:4200"
        elif {"vue", "nuxt"} & dep_names:
            url_hint = "http://localhost:3000"
        elif "http-server" in dep_names or "serve" in dep_names:
            url_hint = "http://localhost:8080"
        # Is it a web app or a node library?
        has_frontend = bool({"react", "vue", "svelte", "next", "nuxt", "@angular/core",
                             "vite", "solid-js", "preact"} & dep_names) or has_index_html
        if has_frontend and dev_cmd:
            return "web", True, {"command": dev_cmd, "url_hint": url_hint or "http://localhost:3000",
                                 "kind": "node-dev"}
        if not has_frontend:
            return "library", False, None
        # frontend but no dev script → static build maybe
        if has_index_html:
            return "static", True, {"command": None, "url_hint": None, "kind": "static-html"}
        return "web", bool(dev_cmd), ({"command": dev_cmd, "url_hint": url_hint, "kind": "node-dev"} if dev_cmd else None)

    # ---- Plain static site ----
    if has_index_html:
        return "static", True, {"command": None, "url_hint": None, "kind": "static-html"}

    # ---- Python ----
    py_manifest = any((root / m).exists() for m in ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"))
    if py_manifest or "Python" in signals:
        txt = ""
        for m in ("pyproject.toml", "setup.py", "requirements.txt"):
            txt += read_text(root / m, limit=20_000).lower()
        # web frameworks
        if any(fw in txt for fw in ("streamlit",)):
            return "web", True, {"command": "streamlit run app.py", "url_hint": "http://localhost:8501", "kind": "streamlit"}
        if any(fw in txt for fw in ("flask",)):
            return "web", True, {"command": "flask run", "url_hint": "http://localhost:5000", "kind": "flask"}
        if any(fw in txt for fw in ("fastapi", "uvicorn")):
            return "web", True, {"command": "uvicorn main:app --reload", "url_hint": "http://localhost:8000", "kind": "fastapi"}
        if any(fw in txt for fw in ("django",)):
            return "web", True, {"command": "python manage.py runserver", "url_hint": "http://localhost:8000", "kind": "django"}
        if any(fw in txt for fw in ("gradio",)):
            return "web", True, {"command": "python app.py", "url_hint": "http://localhost:7860", "kind": "gradio"}
        # CLI with console entry points?
        pyproj = read_text(root / "pyproject.toml", limit=20_000)
        if "console_scripts" in read_text(root / "setup.py") or "[project.scripts]" in pyproj or "console_scripts" in pyproj:
            return "cli", False, None
        # generic python: could be a lib or a script
        return "cli", False, None

    # ---- Rust / Go ----
    if (root / "Cargo.toml").exists():
        return "cli", False, None
    if (root / "go.mod").exists():
        return "cli", False, None

    return "unknown", False, None


def main():
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    out = {"path": str(target)}

    if not target.exists():
        print(json.dumps({"path": str(target), "error": "path does not exist"}))
        sys.exit(1)

    signals = []
    languages = {}
    for f in walk(target):
        rel = f.name
        if rel in {"package.json", "pyproject.toml", "setup.py", "requirements.txt",
                   "Cargo.toml", "go.mod", "SKILL.md", "index.html", "manifest.json",
                   "Dockerfile", "docker-compose.yml"}:
            if rel not in signals:
                signals.append(rel)
        lang = LANG_BY_EXT.get(f.suffix.lower())
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    signal_set = set(signals) | set(languages)

    name, tagline, description, features = extract_readme(target)
    if not name:
        name = target.name.replace("-", " ").replace("_", " ").strip().title() or target.name

    ss_dir = find_screenshots_dir(target)
    screenshots = []
    if ss_dir:
        for child in sorted(ss_dir.iterdir()):
            if child.is_file() and child.suffix.lower() in IMAGE_EXTS:
                screenshots.append(str(child.relative_to(target)).replace("\\", "/"))

    logo = find_logo(target)
    fonts = find_fonts(target)
    rtl, script = detect_rtl(name, tagline, description, " ".join(features),
                             gather_text_sample(target))
    ptype, runnable, run = classify(target, signal_set)

    out.update({
        "name": name,
        "tagline": tagline,
        "description": description,
        "features": features,
        "type": ptype,
        "runnable": runnable,
        "run": run,
        "screenshots_dir": str(ss_dir.relative_to(target)).replace("\\", "/") if ss_dir else None,
        "screenshots": screenshots,
        "logo": str(logo.relative_to(target)).replace("\\", "/") if logo and str(target) in str(logo.resolve()) else (str(logo) if logo else None),
        "fonts": fonts,
        "rtl": rtl,
        "script": script,
        "primary_color": sniff_color(target),
        "languages": dict(sorted(languages.items(), key=lambda x: -x[1])),
        "signals": signals,
    })
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
