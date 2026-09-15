# [H] Squidex vulnerable to Server-Side Request Forgery (SSRF) via URL-based asset upload (/api/apps/{app}/assets)

## Summary
Severity: High
Advisory: CVE-2026-41172
Aliases: GHSA-x7cq-4f4c-8qcv
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41172
Type: osv

## Details
Squidex is an open source headless content management system and content management hub. Prior to version 7.23.0, an SSRF vulnerability allows a user with asset upload permission to force the server to fetch arbitrary URLs, including localhost/private network targets, and persist the response as an asset. Version 7.23.0 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41172.json
- https://github.com/Squidex/squidex/security/advisories/GHSA-x7cq-4f4c-8qcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41172
- https://github.com/Squidex/squidex/commit/b81d75e1d9c1a8e30993c2ee59b350002b9aeda4
