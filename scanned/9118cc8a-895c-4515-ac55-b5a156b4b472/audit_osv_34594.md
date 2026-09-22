# [C] WeGIA SQL Injection via 'id_dependente' param at endpoint `/html/funcionario/dependente_documento.php`

## Summary
Severity: Critical
Advisory: CVE-2025-62360
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-10-13
Source: https://osv.dev/vulnerability/CVE-2025-62360
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users.Prior to 3.5.1, a SQL Injection vulnerability was identified in the /html/funcionario/dependente_documento.php endpoint, specifically in the id_dependente parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This vulnerability is fixed in 3.5.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62360.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-m4j6-q5m4-x24g
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-mwvv-q9gh-gwxm
- https://nvd.nist.gov/vuln/detail/CVE-2025-62360
- https://github.com/LabRedesCefetRJ/WeGIA/issues/310
- https://github.com/LabRedesCefetRJ/WeGIA/commit/7abbffd3915a64b97dde01954222fc0fbd804f70
