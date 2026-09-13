# [C] SQL Injection in query_geracao_auto.php

## Summary
Severity: Critical
Advisory: CVE-2025-30365
Aliases: GHSA-ghx8-h92j-h422
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-30365
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. A SQL Injection vulnerability was identified in versions prior to 3.2.8 in the endpoint /WeGIA/html/socio/sistema/controller/query_geracao_auto.php, specifically in the query parameter. This vulnerability allows the execution of arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. Version 3.2.8 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30365.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-ghx8-h92j-h422
- https://nvd.nist.gov/vuln/detail/CVE-2025-30365
