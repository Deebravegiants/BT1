# [M] glpi Authenticated SQL Injection

## Summary
Severity: Medium
Advisory: CVE-2023-43813
Aliases: GHSA-94c3-fw5r-3362
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-43813
Type: osv

## Details
GLPI is a free asset and IT management software package. Starting in version 10.0.0 and prior to version 10.0.11, the saved search feature can be used to perform a SQL injection. Version 10.0.11 contains a patch for the issue.

## References
- https://github.com/glpi-project/glpi/releases/tag/10.0.11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43813.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-94c3-fw5r-3362
- https://nvd.nist.gov/vuln/detail/CVE-2023-43813
- https://github.com/glpi-project/glpi/commit/4bd7f02d940953b9cbc9d285f7544bb0e490e75e
