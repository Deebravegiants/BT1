# [C] SQL Injection endpoint 'historico_paciente.php' parameter 'id_fichamedica' in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-26617
Aliases: GHSA-f654-c5r5-jx77
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26617
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. A SQL Injection vulnerability was discovered in the WeGIA application, `historico_paciente.php` endpoint. This vulnerability could allow an attacker to execute arbitrary SQL queries, allowing unauthorized access to sensitive information. This issue has been addressed in version 3.2.14 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26617.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-f654-c5r5-jx77
- https://nvd.nist.gov/vuln/detail/CVE-2025-26617
