# [M] Invidious - Cross-User Playlist Video Deletion via Missing Ownership Check

## Summary
Severity: Medium
Advisory: CVE-2026-58447
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58447
Type: osv

## Details
Invidious through 2.20260626.0, fixed in commit 77ad416, contains a broken object level authorization vulnerability that allows authenticated attackers to delete videos from other users' playlists by supplying an arbitrary global video index in the remove_video action of the playlist endpoint. Attackers can obtain per-video index values from the public playlist JSON API and submit them to the playlist video deletion endpoint without ownership validation, permanently removing videos from playlists they do not own.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58447
- https://www.vulncheck.com/advisories/invidious-cross-user-playlist-video-deletion-via-missing-ownership-check
- https://github.com/iv-org/invidious/pull/5790
- https://github.com/iv-org/invidious/commit/77ad41678b45c4f6815940123f1796fc51259f45
- https://github.com/iv-org/invidious
- https://github.com/iv-org/invidious/issues/5777
