# [M] Combodo iTop: Unauthenticated user can delete .readonly file

## Summary
Severity: Medium
Advisory: CVE-2026-34949
Aliases: GHSA-2xh3-r27f-3pr5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-34949
Type: osv

## Details
Combodo iTop is a web based IT service management tool.Prior to 3.2.3, an unauthenticated user could delete the .readonly file on iTop instances — a file created during the setup process that prevents users from performing write actions. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34949.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-2xh3-r27f-3pr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-34949
