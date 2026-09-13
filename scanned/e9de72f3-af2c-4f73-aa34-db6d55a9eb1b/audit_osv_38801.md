# [H] GLPI Vulnerable to Arbitrary Item Deletion via Planning Endpoint

## Summary
Severity: High
Advisory: CVE-2026-42318
Aliases: GHSA-w7mr-3vwm-2j22
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-42318
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 9.5.0 and prior to versions 10.0.25 and 11.0.7, low privilege users with access to planning can delete any object in GLPI. Upgrade to 11.0.7 or 10.0.25 to receive a patch. As a workaround, disable delete rights for User's planning.

## References
- https://vokecyber.com/research/cve-2026-42318-glpi-arbitrary-deletion
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42318.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-w7mr-3vwm-2j22
- https://nvd.nist.gov/vuln/detail/CVE-2026-42318
