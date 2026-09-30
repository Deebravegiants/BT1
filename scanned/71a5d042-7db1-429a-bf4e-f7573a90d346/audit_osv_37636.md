# [H] Tautulli: Unsanitized JSONP callback parameter allows cross-origin script injection and API key theft

## Summary
Severity: High
Advisory: CVE-2026-32275
Aliases: GHSA-95mg-wpqw-9qxh
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-32275
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. From version 1.3.10 to before version 2.17.0, an unsanitized JSONP callback parameter allows cross-origin script injection and API key theft. This issue has been patched in version 2.17.0.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32275.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-95mg-wpqw-9qxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-32275
