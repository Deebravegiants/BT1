# [C] SQL Injection endpoint 'html/personalizacao_upload.php' parameter 'id_campo' in WeGIA

## Summary
Severity: Critical
Advisory: CVE-2025-27096
Aliases: GHSA-j856-wh9m-9vpm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-27096
Type: osv

## Details
WeGIA is a Web Manager for Institutions with a focus on Portuguese language. A SQL Injection vulnerability was discovered in the WeGIA application, personalizacao_upload.php endpoint. This vulnerability allow an authorized attacker to execute arbitrary SQL queries, allowing access to sensitive information. This issue has been addressed in version 3.2.14 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27096.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-j856-wh9m-9vpm
- https://nvd.nist.gov/vuln/detail/CVE-2025-27096
