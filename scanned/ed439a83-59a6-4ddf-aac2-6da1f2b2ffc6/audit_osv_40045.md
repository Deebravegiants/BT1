# [M] Music Player Daemon < 0.24.11 Stack Buffer Overflow via pcm_unpack_24be

## Summary
Severity: Medium
Advisory: CVE-2026-49127
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-49127
Type: osv

## Details
Music Player Daemon (MPD) before version 0.24.11 contains a stack buffer overflow vulnerability in the pcm_unpack_24be function in src/pcm/Pack.cxx that allows unauthenticated attackers to corrupt stack memory by triggering an off-by-one write in the PCM decoder plugin. Attackers can issue two MPD commands referencing a malicious HTTP audio source to cause the unpack loop to write 1366 entries into a 1365-entry buffer, overwriting four bytes past the array boundary with three attacker-controlled bytes from an HTTP response body, resulting in daemon termination or potential code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49127.json
- https://github.com/MusicPlayerDaemon/MPD/releases/tag/v0.24.11
- https://nvd.nist.gov/vuln/detail/CVE-2026-49127
- https://raw.githubusercontent.com/MusicPlayerDaemon/MPD/v0.24.11/NEWS
- https://www.vulncheck.com/advisories/music-player-daemon-stack-buffer-overflow-via-pcm-unpack-24be
- https://github.com/MusicPlayerDaemon/MPD/issues/2485
- https://github.com/MusicPlayerDaemon/MPD/commit/59911028c020f84bc2e669da6a1ef88121301274
- https://www.musicpd.org/news/2026/05/mpd-0-24-11-released/
- https://github.com/MusicPlayerDaemon/MPD
- https://mstreet97.github.io/security-research/opensource/vulnerability-disclosure/cybersecurity/cve/2026/05/25/Four_Bugs_Reachable_nc.html
