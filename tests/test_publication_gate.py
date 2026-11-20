# -*- coding: utf-8 -*-
"""Nothing becomes public except through a gate that read it first.

The surfaces, and who covers them:

    working tree ......... scan_markers         (pre-push, CI, publish)
    commit messages ...... scan_messages        (pre-push)
    PR title / body ...... --text  <- gh_gate.py
    issue / comment ...... --text  <- gh_gate.py
    squash commit message  gh_gate.squash_message, composed LOCALLY so
                           GitHub never builds one out of text nobody read

Run:  python3 test_publication_gate.py
"""
import os
import pathlib
import subprocess
import sys
import tempfile

TOOLS = pathlib.Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
import check_public_set as gate  # noqa: E402
import gh_gate  # noqa: E402

CHECKS = FAILED = 0

#: Built at runtime so this file does not trip the gate it tests.
LEAK = ".".join(["203", "0", "113", "7"])
INNOCENT = "A perfectly ordinary sentence about nothing that anyone owns."


def check(name, ok, detail=""):
    global CHECKS, FAILED
    CHECKS += 1
    if ok:
        print("PASS  %s" % name)
    else:
        FAILED += 1
        print("FAIL  %s%s" % (name, ("  -- " + detail) if detail else ""))


def git(repo, *args, **kw):
    return subprocess.run(("git",) + args, cwd=repo, capture_output=True,
                          text=True, check=True, **kw).stdout


with tempfile.TemporaryDirectory(prefix="gate-") as base:
    repo = os.path.join(base, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.invalid")
    git(repo, "config", "user.name", "Test")
    gate.ROOT = repo

    # --- 1. the tree: an unlisted address is caught, a listed one is not
    leaky = pathlib.Path(repo, "b.py")
    leaky.write_text("# the box at %s\n" % LEAK)
    pathlib.Path(repo, "c.py").write_text("# the LAN at 192.168.1.50\n")
    check("an unlisted IPv4 in a file is caught",
          [h[2] for h in gate.scan_markers()] == [LEAK],
          str(gate.scan_markers()))

    # --- 2. commit messages, which cannot be edited once pushed
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "a clean subject\n\nseen on " + LEAK)
    head = git(repo, "rev-parse", "HEAD").strip()
    check("a commit MESSAGE naming an address is caught",
          len(gate.scan_messages([head])) == 1)
    git(repo, "commit", "-q", "--amend", "--no-edit", "--allow-empty")
    check("`--amend --no-edit` keeps the message, and the gate still sees it",
          len(gate.scan_messages(["HEAD"])) == 1)
    git(repo, "commit", "-q", "--amend", "-m", "a clean subject\n\nown words")
    check("rewording the message clears it", gate.scan_messages(["HEAD"]) == [])
    newer = git(repo, "rev-parse", "HEAD").strip()
    check("--range excludes what the remote already has",
          gate.scan_messages([newer, "^" + newer]) == [])

    # --- 3. --text checks only the text handed in
    dirty = os.path.join(base, "dirty.md")
    clean = os.path.join(base, "clean.md")
    pathlib.Path(dirty).write_text("logs from %s\n" % LEAK)
    pathlib.Path(clean).write_text(INNOCENT + "\n")
    sys.argv = ["check_public_set.py", "--text", dirty]
    check("--text refuses a PR body naming an address", gate.main() == 1)
    sys.argv = ["check_public_set.py", "--text", clean]
    check("--text passes text of our own, whatever the tree holds",
          gate.main() == 0)

    # --- 4. gh_gate pulls the text out of every shape of gh command -------
    def harvested(argv):
        return sorted(flag for flag, _text in gh_gate.harvest(argv)[1])

    check("gh_gate harvests --title and --body",
          harvested(["pr", "create", "--title", "t", "--body", "b"])
          == ["--body", "--title"])
    check("gh_gate harvests --flag=value as well as --flag value",
          harvested(["pr", "create", "--title=t"]) == ["--title"])
    check("gh_gate harvests a --body-file's CONTENTS",
          gh_gate.harvest(["pr", "create", "--body-file", dirty])[1][0][1]
          .strip().endswith(LEAK))
    check("gh_gate harvests gh's short aliases",
          harvested(["issue", "comment", "1", "-b", "x", "-F", clean])
          == ["-F", "-b"])
    check("gh_gate leaves a command with no text alone",
          harvested(["pr", "view", "189", "--json", "title"]) == [])

    # --- 5. the squash merge, which has no text in its command line -------
    argv = ["pr", "merge", "12", "--squash"]
    check("a squash merge carries no text of its own, which is the trap",
          harvested(argv) == [],
          "so gh_gate must compose the message rather than let GitHub do it")


# --- 6. the squash message is composed from FULL commit messages ----------
LONG = ("detail: the season sidebar marks each season, as the Apple TV app "
        "now does")
subject, body = gh_gate.compose_squash("191", "ignored", [LONG + "\n\nThe body."])
check("a long subject survives whole -- GraphQL's messageHeadline truncates it",
      subject == LONG + " (#191)" and "\u2026" not in subject, subject)
check("...and the body does not start with the overflow",
      body == "The body.", repr(body[:40]))
subject, body = gh_gate.compose_squash("7", "The PR title", ["one\n\nfirst", "two"])
check("several commits: the PR title, then each message as GitHub lists them",
      subject == "The PR title (#7)" and body == "* one\n\nfirst\n\n* two", repr(body))

# --- 7. the squash SUBJECT is held to 65, " (#N)" included -------------
try:
    gh_gate.main(["pr", "merge", "203", "--squash", "--subject", "x" * 72])
    refused = ""
except SystemExit as exc:
    refused = str(exc)
check("a squash subject over 65 is refused before anything is sent",
      "subject is 72 chars" in refused, refused)

# --- 8. the squash BODY is held to 8 lines, and composed when not given ---
subject, body = gh_gate.compose_squash("9", "Title", [
    "one\n\nfirst\n\nCo-Authored-By: A <a@x>", "two\n\nCo-Authored-By: A <a@x>"])
check("several commits share one Co-Authored-By, at the end",
      body == "* one\n\nfirst\n\n* two\n\nCo-Authored-By: A <a@x>", repr(body))


def merged(argv, composed):
    """What gh_gate would run for `argv`, with GitHub and gh stubbed out."""
    ran = []
    real = (gh_gate.squash_message, gh_gate.gate, gh_gate.subprocess.run)
    gh_gate.squash_message = lambda number: composed
    gh_gate.gate = lambda blobs: None
    gh_gate.subprocess.run = lambda cmd, **kw: ran.append(cmd) or type("R", (), {"returncode": 0})
    try:
        gh_gate.main(argv)
        return ran[0] if ran else [], ""
    except SystemExit as exc:
        return [], str(exc)
    finally:
        gh_gate.squash_message, gh_gate.gate, gh_gate.subprocess.run = real


cmd, refused = merged(["pr", "merge", "327", "--squash", "--subject", "Short"],
                      ("Composed (#327)", "One line."))
check("a --subject alone still gets a composed --body, so GitHub writes none",
      cmd[-2:] == ["--body", "One line."] and cmd.count("--subject") == 1
      and cmd[cmd.index("--subject") + 1] == "Short", repr(cmd))
long_body = "\n".join("line %d" % i for i in range(13))
cmd, refused = merged(["pr", "merge", "327", "--squash", "--subject", "Short"],
                      ("Composed (#327)", long_body))
check("a composed body over 8 lines is refused before gh runs",
      not cmd and "body is 13 lines" in refused, refused)
cmd, refused = merged(["pr", "merge", "327", "--squash", "--subject", "Short",
                       "--body", long_body], ("unused", ""))
check("...and so is a long --body given by hand", not cmd and "body is 13 lines" in refused,
      refused)
cmd, refused = merged(["pr", "merge", "327", "--squash", "--subject", "Short", "--body",
                       "\n".join("line %d" % i for i in range(8)) + "\n\nCo-Authored-By: A <a@x>"],
                      ("unused", ""))
check("eight lines and a trailer pass", cmd and not refused, refused)

print()
if FAILED:
    print("FAIL: %d of %d" % (FAILED, CHECKS))
    raise SystemExit(1)
print("publication gate: every public surface is read before it is written "
      "(%d checks)" % CHECKS)
