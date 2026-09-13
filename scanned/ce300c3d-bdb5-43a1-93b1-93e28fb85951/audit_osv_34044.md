# [C] WeGIASQL Injection (Blind Time-Based) Vulnerability in idatendido_familiares Parameter on dependente_editarDoc.php Endpoint

## Summary
Severity: Critical
Advisory: CVE-2025-54061
Aliases: GHSA-g47q-vfpj-g9mr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-07-17
Source: https://osv.dev/vulnerability/CVE-2025-54061
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. A SQL Injection vulnerability was identified in versions prior to 3.4.6 in the `idatendido_familiares` parameter of the `/html/funcionario/dependente_editarDoc.php` endpoint. This vulnerability allows attacker to manipulate SQL queries and access sensitive database information, such as table names and sensitive data. Version 3.4.6 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54061.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-g47q-vfpj-g9mr
- https://nvd.nist.gov/vuln/detail/CVE-2025-54061
