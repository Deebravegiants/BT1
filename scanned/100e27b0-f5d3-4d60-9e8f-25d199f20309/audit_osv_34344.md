# [C] WeGIA vulnerable to Blind Time-Based SQL Injection in endpoint 'listar_despachos.php' parameter 'id_memorando'

## Summary
Severity: Critical
Advisory: CVE-2025-58454
Aliases: GHSA-ghfh-g6rg-jmqf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-09-08
Source: https://osv.dev/vulnerability/CVE-2025-58454
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. A SQL Injection vulnerability was identified in WeGIA versions 3.4.10 and prior inthe endpoint /WeGIA/html/memorando/listar_despachos.php, in the id_memorando parameter. This vulnerability allow an authorized attacker to execute arbitrary SQL queries, allowing access to sensitive information. Version 3.4.11 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58454.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-ghfh-g6rg-jmqf
- https://nvd.nist.gov/vuln/detail/CVE-2025-58454
