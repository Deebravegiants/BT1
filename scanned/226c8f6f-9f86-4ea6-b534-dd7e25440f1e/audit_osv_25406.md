# [H] GLPI vulnerable to unauthorized access to Dashboard data

## Summary
Severity: High
Advisory: CVE-2023-35939
Aliases: GHSA-cjcx-pwcx-v34c
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-35939
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 9.5.0 and prior to version 10.0.8, an incorrect rights check on a on a file accessible by an authenticated user (or not for certain actions), allows a threat actor to interact, modify, or see Dashboard data. Version 10.0.8 contains a patch for this issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35939.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-cjcx-pwcx-v34c
- https://nvd.nist.gov/vuln/detail/CVE-2023-35939
