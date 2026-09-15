# [C] WeGIA SQL Injection vulnerability  via 'id_funcionario' param at endpoint `/html/funcionario/dependente_remover.php`

## Summary
Severity: Critical
Advisory: CVE-2025-57761
Aliases: GHSA-fxwc-r5m4-hj62
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-08-21
Source: https://osv.dev/vulnerability/CVE-2025-57761
Type: osv

## Details
WeGIA is a Web manager for charitable institutions. Prior to 3.4.10, there is a SQL Injection vulnerability in the /html/funcionario/dependente_remover.php endpoint, specifically in the id_funcionario parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This vulnerability is fixed in 3.4.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57761.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-fxwc-r5m4-hj62
- https://nvd.nist.gov/vuln/detail/CVE-2025-57761
- http://github.com/LabRedesCefetRJ/WeGIA/commit/baec5c70620b05a09b130a94db8216e3bfe7e4ce
