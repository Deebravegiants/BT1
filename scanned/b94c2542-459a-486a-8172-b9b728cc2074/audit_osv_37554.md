# [H] WeGIA has a SQL Injection via Direct Query Interpolation in restaurar_produto.php

## Summary
Severity: High
Advisory: CVE-2026-31895
Aliases: GHSA-m39r-p62f-vmqm
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31895
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to version 3.6.6, WeGIA (Web gerenciador para instituições assistenciais) contains a SQL injection vulnerability in html/matPat/restaurar_produto.php. The id_produto parameter from $_GET is directly interpolated into SQL queries without parameterization or sanitization. This vulnerability is fixed in 3.6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31895.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-m39r-p62f-vmqm
- https://nvd.nist.gov/vuln/detail/CVE-2026-31895
