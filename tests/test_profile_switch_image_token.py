"""A profile switch drops the cached image token.

The token is minted for one profile, so the next profile must not reuse it.

Run:  python3 test_profile_switch_image_token.py
"""
import time

import kodi_stubs  # noqa: F401  -- installs the Kodi stubs
import xbmcvfs

from resources.lib import auth

RESULTS = []


def check(name, ok):
    RESULTS.append((name, ok))
    print(f"{'PASS' if ok else 'FAIL'}  {name}")


auth.save(auth.Tokens(server="http://a", server_id="s", connect_url="https://c",
                      access_token="t", refresh_token="r", token_type="Bearer",
                      expires_in=3600, obtained_at=time.time(), device_id="d"))


def cached():
    return auth.load_cached_image_token() is not None


auth.save_image_token("img-p1", time.time() + 3600)
check("the image token is cached", cached())

auth.save_profile_selection("p2", None, None)
check("choosing a profile drops it", not cached())
check("the choice itself is saved", auth.load().profile_id == "p2")

auth.save_image_token("img-p2", time.time() + 3600)
auth.clear_profile_selection()
check("forgetting the profile drops it", not cached())
check("the profile is forgotten", auth.load().profile_id is None)

auth.save_image_token("img-x", time.time() + 3600)
auth.save_rotated_profile_token("q", None)
check("a server rotation keeps it (same profile)", cached())

check("file really gone after a switch",
      (auth.save_profile_selection("p3", None, None),
       not xbmcvfs.exists(auth._image_token_file_path()))[1])

failed = [n for n, ok in RESULTS if not ok]
print("\n%d/%d passed" % (len(RESULTS) - len(failed), len(RESULTS)))
raise SystemExit(1 if failed else 0)
