# [M] GLPI vulnerable to unauthorized access to KnowbaseItem data

## Summary
Severity: Medium
Advisory: CVE-2023-34107
Aliases: GHSA-966h-xrf5-pmj4
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-34107
Type: osv

## Details
GLPI is a free asset and IT management software package. Versions of the software starting with 9.2.0 and prior to 10.0.8 have an incorrect rights check on a on a file accessible by an authenticated user, allows access to the view all KnowbaseItems. Version 10.0.8 has a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34107.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-966h-xrf5-pmj4
- https://nvd.nist.gov/vuln/detail/CVE-2023-34107
