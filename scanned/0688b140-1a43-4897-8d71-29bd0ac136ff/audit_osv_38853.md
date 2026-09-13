# [M] Pode: Directory Traversal is possible on Static Routes

## Summary
Severity: Medium
Advisory: CVE-2026-42598
Aliases: GHSA-7rhp-w8fv-h99q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-42598
Type: osv

## Details
Pode is a Cross-Platform PowerShell web framework for creating REST APIs, Web Sites, and TCP/SMTP servers. From 2.4.0, to before 2.13.0, when requesting content from a Static Route, it was possible to request paths such as http://localhost:8080/c:/Windows/System32/drivers/etc/hosts and have the contents returned. This vulnerability is fixed in 2.13.0.

## References
- https://github.com/Badgerati/Pode/security/advisories/GHSA-7rhp-w8fv-h99q
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42598.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42598
- https://github.com/Badgerati/Pode/issues/1667
