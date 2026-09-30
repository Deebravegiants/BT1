# [H] GLPI vulnerable to SQL injection through Computer Virtual Machine information

## Summary
Severity: High
Advisory: CVE-2023-36808
Aliases: GHSA-vf5h-jh9q-2gjm
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-36808
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 0.80 and prior to version 10.0.8, Computer Virtual Machine form and GLPI inventory request can be used to perform a SQL injection attack. Version 10.0.8 has a patch for this issue. As a workaround, one may disable native inventory.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/36xxx/CVE-2023-36808.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-vf5h-jh9q-2gjm
- https://nvd.nist.gov/vuln/detail/CVE-2023-36808
