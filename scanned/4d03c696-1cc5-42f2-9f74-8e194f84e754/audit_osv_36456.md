# [M] GLPI is vulnerable to session stealing on externally authenticated user change

## Summary
Severity: Medium
Advisory: CVE-2026-23624
Aliases: GHSA-5j4j-vx46-r477
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-23624
Type: osv

## Details
GLPI is a free asset and IT management software package. In versions starting from 0.71 to before 10.0.23 and before 11.0.5, when remote authentication is used, based on SSO variables, a user can steal a GLPI session previously opened by another user on the same machine. This issue has been patched in versions .

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.23
- https://github.com/glpi-project/glpi/releases/tag/11.0.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23624.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-5j4j-vx46-r477
- https://nvd.nist.gov/vuln/detail/CVE-2026-23624
