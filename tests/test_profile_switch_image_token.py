"""A profile switch never hands the next profile the last one's image token.

The token is minted for one profile, so choosing or forgetting a profile
drops the cached one, and the cache only answers for the profile it names.

Run:  python3 test_profile_switch_image_token.py
"""
import json
import time

import kodi_stubs  # noqa: F401  -- installs the Kodi stubs
import xbmcvfs

from resources.lib import atomicwrite, auth

RESULTS = []
LATER = time.time() + 3600


def check(name, ok):
    RESULTS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}")


auth.save(auth.Tokens(server="http://a", server_id="s", connect_url="https://c",
                      access_token="t", refresh_token="r", token_type="Bearer",
                      expires_in=3600, obtained_at=time.time(), device_id="d"))


def on_disk():
    return xbmcvfs.exists(auth._image_token_file_path())


auth.save_profile_selection("p1", "pin-1", LATER)
auth.save_image_token("img-p1", LATER, "p1")
check("p1's token is cached for p1", auth.load_cached_image_token("p1") == ("img-p1", LATER))

auth.save_rotated_profile_token("pin-1b", LATER)
check("a server rotation of p1's PIN token keeps it", auth.load().profile_token == "pin-1b"
      and auth.load_cached_image_token("p1") is not None)

auth.save_profile_selection("p2", None, None)
check("switching p1 -> p2 drops it", not on_disk())

auth.save_image_token("img-p1-late", LATER, "p1")
check("a p1 mint landing after the switch is not p2's",
      auth.load_cached_image_token("p2") is None)

auth.save_image_token("img-p2", LATER, "p2")
auth.clear_profile_selection()
check("forgetting the profile drops it", not on_disk())
check("the profile is forgotten", auth.load().profile_id is None)

atomicwrite.write_json(auth._image_token_file_path(), {"token": "old", "expires_at": LATER})
check("a file from before profiles were recorded is not trusted",
      auth.load_cached_image_token("p2") is None and auth.load_cached_image_token(None) is None)

auth.save_image_token("img-primary", LATER, None)
check("no profile (primary) round-trips", auth.load_cached_image_token(None) == ("img-primary", LATER))
with open(xbmcvfs.translatePath(auth._image_token_file_path())) as f:
    check("the file names its profile", json.load(f).get("profile_id") == "")

failed = [n for n, ok in RESULTS if not ok]
print("\n%d/%d passed" % (len(RESULTS) - len(failed), len(RESULTS)))
raise SystemExit(1 if failed else 0)
