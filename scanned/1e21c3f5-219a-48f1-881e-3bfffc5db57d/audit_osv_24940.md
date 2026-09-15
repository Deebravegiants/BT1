# [H] GLPI vulnerable to Privilege Escalation from Technician to Super-Admin

## Summary
Severity: High
Advisory: CVE-2023-28634
Aliases: GHSA-4279-rxmh-gf39
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-05
Source: https://osv.dev/vulnerability/CVE-2023-28634
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.83 and prior to versions 9.5.13 and 10.0.7, a user who has the Technician profile could see and generate a Personal token for a Super-Admin. Using such token it is possible to negotiate a GLPI session and hijack the Super-Admin account, resulting in a Privilege Escalation. Versions 9.5.13 and 10.0.7 contain a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.7
- https://github.com/glpi-project/glpi/releases/tag/9.5.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28634.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-4279-rxmh-gf39
- https://nvd.nist.gov/vuln/detail/CVE-2023-28634
