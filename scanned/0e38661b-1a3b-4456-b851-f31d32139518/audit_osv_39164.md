# [H] GLPI vulnerable to unauthorized reading of a specific asset object

## Summary
Severity: High
Advisory: CVE-2026-44281
Aliases: GHSA-prjc-xwmh-rhxw
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-44281
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.78 and prior to versions 10.0.25 and 11.0.7, an authenticated user with config READ permission can read a specific asset object. Upgrade to 11.0.7 or 10.0.25 to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44281.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-prjc-xwmh-rhxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-44281
