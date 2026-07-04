#!/usr/bin/env python3
"""
pick_theme.py — theme rotation + shortlist for the /mockmeup skill.

Ensures every generated poster uses a DIFFERENT premium theme: it excludes
themes already used for this project and the most-recently used themes globally,
then prints a tag-ranked shortlist. The AI makes the final pick from the
shortlist (needing N distinct themes for N output sizes) and calls `record`
after rendering.

State lives in  <MOCKMEUP_HOME>/theme_history.json  (created on first use):
    { "global": ["id", ...],              # most-recent last
      "projects": { "<project>": ["id"] } }

Subcommands
-----------
  shortlist --project NAME --count N [--tags a,b,c] [--mode dark|light|either] [--size K]
      Print JSON: { "shortlist": [ {id,name,mode,tags,score}, ... ],
                    "excluded_recent": [...], "excluded_project": [...] }
      `--count` = how many DISTINCT themes the run needs (default 2).
      `--size`  = how many candidates to return (default max(6, count*3)).

  record --project NAME --theme ID [--theme ID2 ...]
      Append the chosen theme id(s) to global + project history.

  list [--mode ...] [--tags ...]
      Print the full catalog (optionally filtered).

Exit 0 on success; JSON error on stdout + non-zero on failure. Never errors
just because everything was recently used — it relaxes exclusions instead.
"""
import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = HERE.parent                                   # MOCKMEUP_HOME
CATALOG = HOME / "references" / "themes" / "catalog.json"
HISTORY = HOME / "theme_history.json"

# How many of the most-recent global picks to avoid when possible.
GLOBAL_RECENCY_WINDOW = 6


def load_catalog():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return data["themes"]


def load_history():
    if HISTORY.exists():
        try:
            h = json.loads(HISTORY.read_text(encoding="utf-8"))
        except Exception:
            h = {}
    else:
        h = {}
    h.setdefault("global", [])
    h.setdefault("projects", {})
    return h


def save_history(h):
    HISTORY.write_text(json.dumps(h, indent=2, ensure_ascii=False), encoding="utf-8")


def score(theme, want_tags, want_mode):
    """Higher = better fit. Tag overlap dominates; mode match is a bonus."""
    s = 0
    ttags = set(theme.get("tags", []))
    for t in want_tags:
        if t in ttags:
            s += 10
    if want_mode and want_mode != "either":
        if theme["mode"] == want_mode:
            s += 6
        elif theme["mode"] == "either":
            s += 3
        else:
            s -= 4          # wrong mode is allowed but discouraged
    return s


def shortlist(args):
    themes = load_catalog()
    hist = load_history()
    by_id = {t["id"]: t for t in themes}

    want_tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    want_mode = args.mode
    count = max(1, args.count)
    size = args.size if args.size else max(6, count * 3)

    used_project = list(dict.fromkeys(hist["projects"].get(args.project, [])))
    recent_global = list(dict.fromkeys(hist["global"][-GLOBAL_RECENCY_WINDOW:]))

    def rank(pool):
        scored = sorted(
            pool,
            key=lambda t: (score(by_id[t], want_tags, want_mode), t),
            reverse=True,
        )
        return scored

    all_ids = [t["id"] for t in themes]
    # Tier 1: never used for this project AND not recently used globally.
    tier1 = [i for i in all_ids if i not in used_project and i not in recent_global]
    # Tier 2: relax global recency (still avoid this project's own history).
    tier2 = [i for i in all_ids if i not in used_project and i not in tier1]
    # Tier 3: last resort — allow project repeats, oldest-used first.
    proj_age = {tid: idx for idx, tid in enumerate(used_project)}   # earlier = older
    tier3 = sorted(
        [i for i in all_ids if i not in tier1 and i not in tier2],
        key=lambda i: proj_age.get(i, 0),
    )

    ordered = rank(tier1) + rank(tier2) + tier3
    picked = ordered[:max(size, count)]

    out = {
        "project": args.project,
        "need_distinct": count,
        "shortlist": [
            {**by_id[i], "score": score(by_id[i], want_tags, want_mode)}
            for i in picked
        ],
        "excluded_project_history": used_project,
        "excluded_recent_global": recent_global,
        "advice": "Pick %d DISTINCT ids from the top of the shortlist - one per output size. "
                  "Prefer higher score (better mood fit). Then render, then call: "
                  "pick_theme.py record --project %r --theme <id> [...]" % (count, args.project),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def record(args):
    themes = load_catalog()
    valid = {t["id"] for t in themes}
    bad = [t for t in args.theme if t not in valid]
    if bad:
        print(json.dumps({"ok": False, "error": "unknown theme id(s): %s" % bad}))
        sys.exit(1)
    hist = load_history()
    for tid in args.theme:
        hist["global"].append(tid)
        hist["projects"].setdefault(args.project, []).append(tid)
    # keep global history from growing without bound
    hist["global"] = hist["global"][-200:]
    save_history(hist)
    print(json.dumps({"ok": True, "recorded": args.theme, "project": args.project,
                      "history_file": str(HISTORY)}, ensure_ascii=False))


def list_cmd(args):
    themes = load_catalog()
    want_tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]
    rows = []
    for t in themes:
        if args.mode and args.mode != "either" and t["mode"] not in (args.mode, "either"):
            continue
        if want_tags and not (set(want_tags) & set(t.get("tags", []))):
            continue
        rows.append(t)
    print(json.dumps({"count": len(rows), "themes": rows}, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Theme rotation for /mockmeup")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("shortlist")
    sp.add_argument("--project", required=True)
    sp.add_argument("--count", type=int, default=2, help="distinct themes the run needs")
    sp.add_argument("--size", type=int, default=0, help="candidates to return (default max(6,count*3))")
    sp.add_argument("--tags", default="", help="comma list of mood tags to prefer")
    sp.add_argument("--mode", default="", choices=["", "dark", "light", "either"])
    sp.set_defaults(func=shortlist)

    rp = sub.add_parser("record")
    rp.add_argument("--project", required=True)
    rp.add_argument("--theme", action="append", required=True, help="repeatable")
    rp.set_defaults(func=record)

    lp = sub.add_parser("list")
    lp.add_argument("--tags", default="")
    lp.add_argument("--mode", default="", choices=["", "dark", "light", "either"])
    lp.set_defaults(func=list_cmd)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
