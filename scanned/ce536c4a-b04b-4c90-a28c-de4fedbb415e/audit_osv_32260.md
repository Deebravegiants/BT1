# [C] SQL Injection endpoint 'restaurar_produto_desocultar.php' parameter 'id_produto' in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-26610
Aliases: GHSA-6p7c-9hcx-jpqj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26610
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. A SQL Injection vulnerability was discovered in the WeGIA application, `restaurar_produto_desocultar.php` endpoint. This vulnerability allow an authorized attacker to execute arbitrary SQL queries, allowing access to sensitive information. This issue has been addressed in version 3.2.13 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26610.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-6p7c-9hcx-jpqj
- https://nvd.nist.gov/vuln/detail/CVE-2025-26610
