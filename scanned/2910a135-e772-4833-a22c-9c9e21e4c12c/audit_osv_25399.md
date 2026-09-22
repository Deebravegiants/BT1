# [H] GLPI vulnerable to SQL injection via inventory agent request

## Summary
Severity: High
Advisory: CVE-2023-35924
Aliases: GHSA-gxh4-j63w-8jmm
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-35924
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 10.0.0 and prior to version 10.0.8, GLPI inventory endpoint can be used to drive a SQL injection attack. By default, GLPI inventory endpoint requires no authentication. Version 10.0.8 has a patch for this issue. As a workaround, one may disable native inventory.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35924.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-gxh4-j63w-8jmm
- https://nvd.nist.gov/vuln/detail/CVE-2023-35924
