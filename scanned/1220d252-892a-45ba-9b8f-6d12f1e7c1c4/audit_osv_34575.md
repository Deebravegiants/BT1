# [C] WeGIA vulnerable to SQL Injection via 'id_funcionario' param at endpoint `/html/funcionario/dependente_listar.php`

## Summary
Severity: Critical
Advisory: CVE-2025-62177
Aliases: GHSA-4wrg-g9cj-hjcx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-10-13
Source: https://osv.dev/vulnerability/CVE-2025-62177
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. Prior to 3.5.1, a SQL Injection vulnerability was identified in the /html/funcionario/dependente_listar.php endpoint, specifically in the id_funcionario parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This vulnerability is fixed in 3.5.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62177.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-4wrg-g9cj-hjcx
- https://nvd.nist.gov/vuln/detail/CVE-2025-62177
- https://github.com/LabRedesCefetRJ/WeGIA/commit/017fdd71380ab898570752aebc3fe1ef318a5d0d
