# [M] MyTube has Rate Limiting Bypass via X-Forwarded-For Header Spoofing

## Summary
Severity: Medium
Advisory: CVE-2026-23848
Aliases: GHSA-59gr-529g-x45h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23848
Type: osv

## Details
MyTube is a self-hosted downloader and player for several video websites. Prior to version 1.7.71, a rate limiting bypass via `X-Forwarded-For` header spoofing allows unauthenticated attackers to bypass IP-based rate limiting on general API endpoints. Attackers can spoof client IPs by manipulating the `X-Forwarded-For` header, enabling unlimited requests to protected endpoints, including general API endpoints (enabling DoS) and other rate-limited functionality. Version 1.7.71 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23848.json
- https://github.com/franklioxygen/MyTube/security/advisories/GHSA-59gr-529g-x45h
- https://nvd.nist.gov/vuln/detail/CVE-2026-23848
- https://github.com/franklioxygen/MyTube/commit/bc057458804ae7ac70ea00605680512ed3d4257b
