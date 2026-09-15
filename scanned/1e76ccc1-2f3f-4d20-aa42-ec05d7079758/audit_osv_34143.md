# [C] WeGIA SQL Injection via id_fichamedica at endpoint `GET/html/funcionario/dependente_remover.php`

## Summary
Severity: Critical
Advisory: CVE-2025-55167
Aliases: GHSA-4fqm-ww3v-6mwv
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-08-12
Source: https://osv.dev/vulnerability/CVE-2025-55167
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. Prior to version 3.4.8, a SQL Injection vulnerability was identified in the /html/funcionario/dependente_remover.php endpoint, specifically in the id_dependente parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This issue has been patched in version 3.4.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55167.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-4fqm-ww3v-6mwv
- https://nvd.nist.gov/vuln/detail/CVE-2025-55167
- https://github.com/LabRedesCefetRJ/WeGIA/commit/cb7f5e2b98ef6087b80659627f368612e3c535f3
