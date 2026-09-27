# [C] WeGIA has a Time-Based Blind SQL Injection in  remover_produto_ocultar.php

## Summary
Severity: Critical
Advisory: CVE-2026-31896
Aliases: GHSA-w7g3-87cr-8m83
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31896
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Prior to version 3.6.6, a critical SQL injection vulnerability exists in the WeGIA application. The remover_produto_ocultar.php script uses extract($_REQUEST) to populate local variables and then directly concatenates these variables into a SQL query executed via PDO::query. This allows an authenticated (or auth-bypassed) attacker to execute arbitrary SQL commands. This can be used to exfiltrate sensitive data from the database or, as demonstrated in this PoC, cause a time-based delay (denial of service). This vulnerability is fixed in 3.6.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31896.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-w7g3-87cr-8m83
- https://nvd.nist.gov/vuln/detail/CVE-2026-31896
