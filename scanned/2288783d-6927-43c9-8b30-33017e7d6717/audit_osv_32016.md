# [C] WeGIA SQL Injection (Blind Time-Based) endpoint 'verificar_recursos_cargo.php' parameter 'cargo'

## Summary
Severity: Critical
Advisory: CVE-2025-22141
Aliases: GHSA-w7hp-2w2c-p636
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2025-22141
Type: osv

## Details
WeGIA is a web manager for charitable institutions. A SQL Injection vulnerability was identified in the /dao/verificar_recursos_cargo.php endpoint, specifically in the cargo parameter. This vulnerability allows attackers to execute arbitrary SQL commands, compromising the confidentiality, integrity, and availability of the database. This vulnerability is fixed in 3.2.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22141.json
- https://github.com/nilsonLazarin/WeGIA/security/advisories/GHSA-w7hp-2w2c-p636
- https://nvd.nist.gov/vuln/detail/CVE-2025-22141
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-w7hp-2w2c-p636
