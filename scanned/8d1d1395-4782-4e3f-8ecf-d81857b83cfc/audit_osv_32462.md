# [C] WeGIA SQL Injection Vulnerability in nextPage Parameter on control.php Endpoint

## Summary
Severity: Critical
Advisory: CVE-2025-30367
Aliases: GHSA-7j9v-xgmm-h7wr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-30367
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. A SQL Injection vulnerability was identified in versions prior to 3.2.6 in the nextPage parameter of the /WeGIA/controle/control.php endpoint. This vulnerability allows attacker to manipulate SQL queries and access sensitive database information, such as table names and sensitive data. Version 3.2.6 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30367.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-7j9v-xgmm-h7wr
- https://nvd.nist.gov/vuln/detail/CVE-2025-30367
