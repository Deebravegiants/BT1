# [C] SQL Injection endpoint 'salvar_cargo.php' parameter 'id_cargo' in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-24902
Aliases: GHSA-pg73-w9vx-8mgp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2025-24902
Type: osv

## Details
WeGIA is a Web Manager for Charitable Institutions. A SQL Injection vulnerability was discovered in the WeGIA application, `salvar_cargo.php` endpoint. This vulnerability could allow an authorized attacker to execute arbitrary SQL queries, allowing access to  or deletion of sensitive information. This issue has been addressed in version 3.2.12 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24902.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-pg73-w9vx-8mgp
- https://nvd.nist.gov/vuln/detail/CVE-2025-24902
- https://github.com/LabRedesCefetRJ/WeGIA/commit/f535e873a8f26fe413d21f22e3eacc8c79b2fa7f
