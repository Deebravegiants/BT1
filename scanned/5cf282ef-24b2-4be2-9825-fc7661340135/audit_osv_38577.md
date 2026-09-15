# [M] Tautulli Vulnerable to Authenticated Path Traversal in Cache Deletion API

## Summary
Severity: Medium
Advisory: CVE-2026-40605
Aliases: GHSA-fg46-xx7h-mhwr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N/E:P)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-40605
Type: osv

## Details
Tautulli is a Python based monitoring and tracking tool for Plex Media Server. Prior to version 2.17.1, a path traversal vulnerability in the cache deletion endpoint allows authenticated API access to delete directories outside the configured cache path. This can cause arbitrary data loss and service disruption. Version 2.17.1 fixes the issue.

## References
- https://github.com/Tautulli/Tautulli/releases/tag/v2.17.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40605.json
- https://github.com/Tautulli/Tautulli/security/advisories/GHSA-fg46-xx7h-mhwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40605
