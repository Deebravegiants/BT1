# [H] GLPI vulnerable to arbitrary files deletion by technician

## Summary
Severity: High
Advisory: CVE-2026-42317
Aliases: GHSA-jf72-cvjh-px5w
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-42317
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.78 and prior to versions 10.0.25 and 11.0.7, a technician can delete arbitrary files from the filesystem as long as the webserver has write rights on them. Upgrade to 10.0.25 or 11.0.7 to receive a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42317.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-jf72-cvjh-px5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-42317
