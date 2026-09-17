# [M] Music Player Daemon < 0.24.11 Path Traversal via LocalStorage URI Handling

## Summary
Severity: Medium
Advisory: CVE-2026-49128
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-49128
Type: osv

## Details
Music Player Daemon (MPD) before version 0.24.11 contains a path traversal vulnerability in LocalStorage::MapFSOrThrow and LocalStorage::MapUTF8 within the local storage plugin, where the on-disk path is constructed by joining the storage root with a user-supplied URI as plain strings without canonicalization, allowing '..' segments to survive into the resolved path and be flattened by the kernel at openat() time. An unauthenticated attacker can exploit this flaw using the listfiles command to enumerate names, sizes, and modification times of arbitrary directories readable by the MPD process, and the albumart command to read image files in any attacker-chosen directory outside the configured music_directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49128.json
- https://github.com/MusicPlayerDaemon/MPD/releases/tag/v0.24.11
- https://nvd.nist.gov/vuln/detail/CVE-2026-49128
- https://raw.githubusercontent.com/MusicPlayerDaemon/MPD/v0.24.11/NEWS
- https://www.vulncheck.com/advisories/music-player-daemon-path-traversal-via-localstorage-uri-handling
- https://github.com/MusicPlayerDaemon/MPD/issues/2484
- https://github.com/MusicPlayerDaemon/MPD/commit/0b5315b9e5a42cb0e88bf46a7579bb5641543f60
- https://www.musicpd.org/news/2026/05/mpd-0-24-11-released/
- https://github.com/MusicPlayerDaemon/MPD
- https://mstreet97.github.io/security-research/opensource/vulnerability-disclosure/cybersecurity/cve/2026/05/25/Four_Bugs_Reachable_nc.html
