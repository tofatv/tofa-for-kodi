# Changelog prose waiting for a version

End-user release notes for work that is merged on `main` but not released.
`changelog.txt` is strictly version-headed (`release.py:changelog_entries()`
reads it as `[(version, body)]`), and `release.py check`, which CI runs on
every push, fails when its newest heading is ahead of `addon.xml`. So prose
waits here until a version is chosen, and moves across as part of the
release.

## At release time

1. Paste the block below at the TOP of `plugin.video.tofa/changelog.txt`
   under a `<v>` heading.
2. `python3 tools/release.py set <v>`, which refuses without that entry,
   bumps `addon.xml` and re-derives `<news>` (never hand-edited).
3. Delete the entry from this file once it has shipped.

The rest of the procedure is under "Cutting a release" in `CONTRIBUTING.md`.

---

## The block, ready to paste

Nothing parked.

(Everything parked here has shipped. **1.5.1** (2026-11-20) the handover to tofa and kodi.tofa.tv. **1.5.0** (2026-11-03) the server 0.13.0 floor: the Ready to binge row, requests and Browse following the server, Discover off (#348). **1.4.2** (2026-10-28) the library Home row and the genre row by remote (#345), Home rows from newer apps kept (#344). **1.4.1** (2026-10-26) Discover's tabs after Coming Up and Coming Up reached along the tabs (#340), the presentation in version labels (#339). **1.4.0** (2026-10-20) Coming Up's film posters and Who's watching focus at a cold start (#333), Discover filters kept on the profile and the filter focus fix (#335); font set 38. **1.3.0** (2026-10-20) Discover as app 2.1.0 with the Coming Up planner (#327), Continue the saga and universes (#320, #321, #323, #324), Request missing (#326, #330), the card menus and marks (#316, #322, #325), title-page shelf menus and the film edition (#311, #313-#315), the Browse sections row and Back to Home (#318, #319), Missing episodes (#317) and quality rows by height (#329); font set 37. **1.2.0** (2026-10-19) the server 0.12.0 floor (#302), subtitle roles (#303), the person page from PersonPage (#304), Missing episodes (#305), Browse sections (#306) and Seen it / Not interested (#307, #308). **1.1.1** (2026-10-11) the Browse backdrop speeds and dip (#296), Watchlist sorting (#297), the episode row kept on screen (#298), smaller posters and a fuller Videos wall (#299). **1.1.0** (2026-10-10) household viewing and Account as app 2.0 (#284, #289), the cloud sign-in fix (#285), the unreachable-server notice (#286), Settings' four choices (#288), filters inside a collection (#290), Collections sort and the A-Z rail at the app's size (#291), History paging and gone titles (#292, #293). **1.0.0** (2026-10-09) the Apple TV app 2.0 parity pass (#262-#280) and the top bar's Down after an early move off Home (#281). **0.9.38** (2026-10-01) the 0.11.0 floor and the related list taken as final (#238), search collections of every kind (#239), folder browsing (#240, #243), cast photos from the server (#241), Profile 5 converted where Kodi cannot decode it (#242), split-file playback (#244, #245) and picture subtitles before they are prepared (#246). **0.9.37** (2026-09-29) search finding your own collections (#235). **0.9.36** (2026-09-27) related titles asked for again when they come back empty (#223), Home's capability check off the remote's thread (#226) and "Plays as" following Kodi's own mode search (#228-#231). **0.9.35** (2026-09-22) the faster Options and playback start (#213, #214), the failure card's title, Try again and Lower quality (#215, #217), the converted stream's subtitle switch (#220), the collection strip (#212), the profile screen (#216, #218), the partial-season tally (#219) and the Settings and seek-toast spec pass (#210, #211). **0.9.34** (2026-09-22) styled subtitles and their fonts when the server converts (#201, #202), picture subtitles once the server has them ready (#205, #206) and the first card's glow (#207). **0.9.33** (2026-09-21) sign-in renewal through the server during an outage (#197) and the splash stuck behind a dialog (#196). **0.9.32** (2026-09-21) seeking in bursts (#184), the server's own refusal (#185), the season list's marks and not-in-library cards (#186, reworked #191), the profile tiles (#187) and the lone episode's seek pair (#188). **0.9.31** (2026-09-20) the scrub
preview drawn at the programme's own shape (#177), a chapter "named" with
its own timestamp (#176), the Continue Watching hero's year (#178), the
stats panel's subtitle row (#179) and the server floor at 0.10.0.
**0.9.30** (2026-09-18) the region
picker served and alphabetical (#169, #170), the monogram disc taking the
profile's own colour (#172) and the segment-action pill that could disagree
with the player (#168). **0.9.29** (2026-09-17) the skip
pill auto-hide (#161), the Detail hero taking the episode's year and
runtime (#162) and the Media cards spoiler toggle (#163). **0.9.28** (2026-09-03) the update-swap
toast's second cause (#155) and Home rows parity with the apps (#156).
**0.9.27** (2026-09-03) playback
telemetry for the server's Activity page (#149-#151), the single stop
message (#152) and the 0.9.35 floor (#148). **0.9.26** (2026-09-02) the fonts moving
into their own `resource.font.tofa` add-on instead of being copied into the
user's skin (#144), and the Addon handle taken on first use so an update no
longer shows an error toast (#143). **0.9.25** (2026-09-01) the Detail pager
that took two Up presses, the marquee on Detail's episode and cast cards, and
Remove from Continue Watching keeping its slot (#140). **0.9.24** (2026-08-31)
the player tick cost (#135) and the Rewatch icon (#137). **0.9.23** (2026-08-30) the 0.9.34 server floor (#130), the aspect chip on already-matted files (#131) and the HDR10+ "Plays as" fix (#132). **0.9.14** (2026-08-24) the four
0.9.33 adoptions: embedded VobSub (#89), custom collections in Browse
(#90), the subtitle fallback chain (#91) and the converter-start retry
(#92). **0.9.13** (PR #85)
the timeout copy (#81), Cast & Crew and Search's People shelf (#83), Discover
and Collections (#84), and the threads/sockets a closed screen used to keep
(#83). **0.9.12** (2026-08-21) the blank page
after an idle break and the error card that replaced it (PR #76), plus the
two things drawn just past the screen edge (#74/#75). **0.9.11**
(2026-08-19) the audio language on the next episode (#67, PRs #68/#70/#71).
**0.9.10** the same day the hero title (#56), VobSub sidecar subtitles
(#60), HEVC when the server converts (#59) and the server floor at 0.9.32
(#58).)
