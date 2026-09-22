# [H] Missing Authorization on Immich Trip Photo Routes in TREK

## Summary
Severity: High
Advisory: CVE-2026-40185
Aliases: GHSA-pcr3-6647-jh72
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40185
Type: osv

## Details
TREK is a collaborative travel planner. Prior to 2.7.2, TREK was missing authorization checks on the Immich trip photo management routes. This vulnerability is fixed in 2.7.2.

## References
- https://github.com/mauriceboe/TREK/releases/tag/v2.7.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40185.json
- https://github.com/mauriceboe/TREK/security/advisories/GHSA-pcr3-6647-jh72
- https://nvd.nist.gov/vuln/detail/CVE-2026-40185
- https://github.com/mauriceboe/TREK/commit/16277a3811a00c2983f7486fee83c112986cb179
