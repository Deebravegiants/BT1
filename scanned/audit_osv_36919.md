# [H] Music Assistant Server Path Traversal in Playlist Update API Allows Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2026-26975
Aliases: GHSA-7jcc-p6xr-835j
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-26975
Type: osv

## Details
Music Assistant is an open-source media library manager that integrates streaming services with connected speakers. Versions 2.6.3 and below allow unauthenticated network-adjacent attackers to execute arbitrary code on affected installations. The music/playlists/update API allows users to bypass the .m3u extension enforcement and write files anywhere on the filesystem, which is exacerbated by the container running as root. This can be exploited to achieve Remote Code Execution by writing a malicious .pth file to the Python site-packages directory, which will execute arbitrary commands when Python loads. This issue has been fixed in version 2.7.0.

## References
- https://github.com/music-assistant/server/releases/tag/2.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26975.json
- https://github.com/music-assistant/server/security/advisories/GHSA-7jcc-p6xr-835j
- https://nvd.nist.gov/vuln/detail/CVE-2026-26975
- https://github.com/music-assistant/server/pull/2684
