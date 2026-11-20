"""Does anything about to go public name our network, our boxes or us?

Every IPv4 literal and private identifier, matched as patterns over the whole
working tree, the commits being pushed, and any text handed in with `--text`
(a PR body, an issue comment, release notes; `tools/gh_gate.py` uses that).
IPs are checked against an allowlist, because the address that matters is
the one nobody has typed yet. Exit status is 1 while anything is found.

    python3 tools/check_public_set.py                 tree + unpushed commits
    python3 tools/check_public_set.py --range "A..B"  exactly these commits
    python3 tools/check_public_set.py --text body.md  only this text
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: `.yml` is here for the CI workflow, which can name a box as well as any
#: comment can.
TEXT_SUFFIXES = (".py", ".xml", ".txt", ".md", ".html", ".svg", ".json",
                 ".yml")

#: The only IPv4 literals allowed to appear.
ALLOWED_IPS = {
    "192.168.1.50",   # the documentation LAN address, several docstrings
    "10.0.0.5",       # a second private address, test_direct_only only
    "0.0.0.0", "127.0.0.1", "255.255.255.255",
}
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

#: (pattern, what it is). Hardware MODEL names are deliberately absent: naming
#: the box a measurement was taken on is what makes the measurement useful.
MARKER_PATTERNS = [
    (re.compile(r"cinemaone\.ch", re.I), "a personal email domain"),
    (re.compile(r"\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b", re.I), "a MAC address"),
    # Case-sensitive: `/Users/<name>` is a macOS home, `/users/me` an API path.
    (re.compile(r"/Users/[a-z]+"), "a path on someone's machine"),
]

#: Lines where a marker is the subject rather than a leak.
MARKER_EXEMPT = re.compile(
    r"MARKER_PATTERNS|ALLOWED_IPS|a box hostname|a server name|a surname"
    r"|a personal email domain|a real server uuid|a MAC address"
    r"|a path on someone's machine")

#: Build output, caches, local settings, and the published channel (a copy of
#: the add-on, so scanning it reports every finding twice).
SKIP_DIRS = {".git", "__pycache__", "dist", ".claude", "docs", ".venv",
             "node_modules"}


def marker_hits(text: str) -> list[tuple[str, str]]:
    """(match, why) for every marker in free text."""
    hits = [(a, "an IPv4 address not on the allowlist")
            for a in IPV4_RE.findall(text or "") if a not in ALLOWED_IPS]
    for pattern, why in MARKER_PATTERNS:
        hits += [(m.group(0), why) for m in pattern.finditer(text or "")]
    return hits


def candidates() -> list[str]:
    """Every text file in this checkout, which is public by construction."""
    found = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        found += [os.path.join(base, n) for n in files
                  if n.endswith(TEXT_SUFFIXES)]
    return sorted(set(found))


def read(path: str) -> str | None:
    try:
        with open(path, encoding="utf8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return None


def _git(*args: str) -> str:
    try:
        return subprocess.run(("git",) + args, cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return ""


def scan_markers() -> list[tuple[str, int, str, str]]:
    """(relative path, line, what was found, why it is flagged)."""
    found = []
    for path in candidates():
        if os.path.abspath(path) == os.path.abspath(__file__):
            continue  # the patterns themselves live here
        text = read(path)
        if text is None:
            continue
        rel = os.path.relpath(path, ROOT)
        for line_no, line in enumerate(text.splitlines(), 1):
            if MARKER_EXEMPT.search(line):
                continue
            for hit, why in marker_hits(line):
                found.append((rel, line_no, hit, why))
    return found


def scan_messages(revs: list[str]) -> list[tuple[str, int, str, str]]:
    """Markers in the given commits' messages, which cannot be edited once
    pushed."""
    found = []
    for entry in _git("log", "--format=%h %s%x00%B%x01", *revs).split("\x01"):
        head, _, body = entry.strip().partition("\x00")
        found += [("commit " + head[:60], 0, h, w) for h, w in marker_hits(body)]
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--range", dest="rev_range", metavar="REVS",
                        help="scan exactly these commits (rev-list arguments, "
                             "as the pre-push hook builds them) instead of "
                             "the unpushed ones")
    parser.add_argument("--text", nargs="+", metavar="FILE", default=[],
                        help="check only these files of candidate text")
    args = parser.parse_args()

    found = []
    if args.text:
        for path in args.text:
            label = "text %s" % path
            found += [(label, 0, h, w) for h, w in marker_hits(read(path) or "")]
    else:
        print("checking the %d file(s) in the public set" % len(candidates()))
        found += scan_markers()
        revs = (args.rev_range.split() if args.rev_range
                else ["HEAD", "--not", "--remotes=origin"])
        found += scan_messages(revs)

    for rel, line, hit, why in found:
        print("%s:%d  %s -- %s" % (rel, line, hit, why))
    print("MARKERS: %d private identifier(s)" % len(found))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
