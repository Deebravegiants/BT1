# [C] WeGIA SQL Injection via 'cpf' param at endpoint `/html/funcionario/cadastro_funcionario_pessoa_existente.php`

## Summary
Severity: Critical
Advisory: CVE-2025-62179
Aliases: GHSA-x36x-x5j4-wfjf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-13
Source: https://osv.dev/vulnerability/CVE-2025-62179
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. Prior to 3.5.1, a SQL Injection vulnerability was identified in the /html/funcionario/cadastro_funcionario_pessoa_existente.php endpoint, specifically in the cpf parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This vulnerability is fixed in 3.5.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62179.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-x36x-x5j4-wfjf
- https://nvd.nist.gov/vuln/detail/CVE-2025-62179
- https://github.com/LabRedesCefetRJ/WeGIA/commit/885972c55c3a06b5275120e88bb1113754a63b26
