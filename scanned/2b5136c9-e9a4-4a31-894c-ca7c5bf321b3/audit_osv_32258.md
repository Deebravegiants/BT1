# [C] SQL Injection endpoint 'informacao_adicional.php' parameter 'id_descricao' in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-26606
Aliases: GHSA-rxjr-cw9q-cwwg
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-26606
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. A SQL Injection vulnerability was discovered in the WeGIA application, `informacao_adicional.php` endpoint. This vulnerability could allow an attacker to execute arbitrary SQL queries, allowing unauthorized access to sensitive information. This issue has been addressed in version 3.2.13 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26606.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-rxjr-cw9q-cwwg
- https://nvd.nist.gov/vuln/detail/CVE-2025-26606
