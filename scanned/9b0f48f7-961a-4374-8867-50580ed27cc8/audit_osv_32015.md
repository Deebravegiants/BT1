# [C] WeGIA SQL Injection (Blind Time-Based) endpoint 'dependente_listar_um.php' parameter 'id_dependente'

## Summary
Severity: Critical
Advisory: CVE-2025-22140
Aliases: GHSA-mrhp-wfp2-59h5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2025-22140
Type: osv

## Details
WeGIA is a web manager for charitable institutions. A SQL Injection vulnerability was identified in the /html/funcionario/dependente_listar_um.php endpoint, specifically in the id_dependente parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This vulnerability is fixed in 3.2.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22140.json
- https://github.com/nilsonLazarin/WeGIA/security/advisories/GHSA-mrhp-wfp2-59h5
- https://nvd.nist.gov/vuln/detail/CVE-2025-22140
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-mrhp-wfp2-59h5
