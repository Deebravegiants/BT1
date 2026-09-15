# [C] WeGIA SQL Injection via id_fichamedica at endpoint `GET /html/saude/aplicar_medicamento.php`

## Summary
Severity: Critical
Advisory: CVE-2025-55168
Aliases: GHSA-6wjm-c879-pjf6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-08-12
Source: https://osv.dev/vulnerability/CVE-2025-55168
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. Prior to version 3.4.8, a SQL Injection vulnerability was identified in the /html/saude/aplicar_medicamento.php endpoint, specifically in the id_fichamedica parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This issue has been patched in version 3.4.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55168.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-6wjm-c879-pjf6
- https://nvd.nist.gov/vuln/detail/CVE-2025-55168
- https://github.com/LabRedesCefetRJ/WeGIA/issues/245
- https://github.com/LabRedesCefetRJ/WeGIA/commit/766f9f07ff6faee394e0f85d0650f86f8a9248a7https://github.com/LabRedesCefetRJ/WeGIA/commit/766f9f07ff6faee394e0f85d0650f86f8a9248a7
