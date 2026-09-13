# [C] WeGIA has Unauthenticated Time-Based Blind SQL Injection in almox Parameter

## Summary
Severity: Critical
Advisory: CVE-2025-53091
Aliases: GHSA-pmf9-2rc3-vvxx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-06-27
Source: https://osv.dev/vulnerability/CVE-2025-53091
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. A Time-Based Blind SQL Injection vulnerability was discovered in version 3.3.3 the almox parameter of the `/controle/getProdutosPorAlmox.php` endpoint. This issue allows any unauthenticated attacker to inject arbitrary SQL queries, potentially leading to unauthorized data access or further exploitation depending on database configuration. Version 3.4.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53091.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-pmf9-2rc3-vvxx
- https://nvd.nist.gov/vuln/detail/CVE-2025-53091
