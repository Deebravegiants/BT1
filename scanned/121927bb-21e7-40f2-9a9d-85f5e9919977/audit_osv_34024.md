# [C] WeGIA vulnerable to SQL Injection (Blind Time-Based) in `processa_deletar_socio.php` parameter `id_socio`

## Summary
Severity: Critical
Advisory: CVE-2025-53823
Aliases: GHSA-p8xr-qg3c-6ww2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-07-14
Source: https://osv.dev/vulnerability/CVE-2025-53823
Type: osv

## Details
WeGIA is an open source web manager with a focus on the Portuguese language and charitable institutions. Versions prior to 3.4.5 have a SQL Injection vulnerability in the endpoint `/WeGIA/html/socio/sistema/processa_deletar_socio.php`, in the `id_socio` parameter. This vulnerability allows the execution of arbitrary SQL commands, which can compromise the confidentiality, integrity, and availability of stored data. Version 3.4.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53823.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-p8xr-qg3c-6ww2
- https://nvd.nist.gov/vuln/detail/CVE-2025-53823
