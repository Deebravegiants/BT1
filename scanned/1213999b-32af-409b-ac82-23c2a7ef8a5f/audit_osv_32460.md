# [C] WeGIA vulnerable to SQL Injection (Blind Time-Based) in remuneracao.php parameter id_funcionario

## Summary
Severity: Critical
Advisory: CVE-2025-30364
Aliases: GHSA-x3ff-5qp7-43qv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-30364
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. A SQL Injection vulnerability was identified in versions prior to 3.2.8 in the endpoint /WeGIA/html/funcionario/remuneracao.php, in the id_funcionario parameter. This vulnerability allows the execution of arbitrary SQL commands, which can compromise the confidentiality, integrity, and availability of stored data. Version 3.2.8 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30364.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-x3ff-5qp7-43qv
- https://nvd.nist.gov/vuln/detail/CVE-2025-30364
