# [H] OpenCode Studio < 2.4.4 Unauthenticated File Read via /api/tmp and /api/music

## Summary
Severity: High
Advisory: CVE-2026-69110
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-69110
Type: osv

## Details
OpenCode Studio before 2.4.4 contains a missing authentication vulnerability that allows unauthenticated remote attackers to read arbitrary files within the temp and static/music directories by directly accessing the GET /api/tmp/:tmpFile and GET /api/music/:fileName endpoints. Attackers can retrieve intermediate audio, video artifacts, and subtitles belonging to other users' jobs, and additionally delete any video by ID through the unauthenticated DELETE /api/short-video/:videoId endpoint.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69110.json
- https://github.com/Microck/opencode-studio/releases/tag/v2.4.4
- https://nvd.nist.gov/vuln/detail/CVE-2026-69110
- https://www.vulncheck.com/advisories/opencode-studio-unauthenticated-file-read-via-api-tmp-and-api-music
- https://github.com/Microck/opencode-studio/pull/55
- https://github.com/Microck/opencode-studio/commit/1f4d7a7f52beb43105d345b26fd0c0ffc2bf0004
- https://github.com/Microck/opencode-studio
- https://github.com/Microck/opencode-studio/issues/54
