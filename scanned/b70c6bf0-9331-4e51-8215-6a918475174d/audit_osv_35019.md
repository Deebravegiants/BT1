# [C] WeGIA is vulnerable to SQL Injection via editar_categoria endpoint parameter

## Summary
Severity: Critical
Advisory: CVE-2025-67501
Aliases: GHSA-hj2x-qfm3-2869
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-67501
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. Versions 3.5.4 and below contain an SQL Injection vulnerability in the /html/matPat/editar_categoria.php endpoint. The application fails to properly validate and sanitize user inputs in the id_categoria parameter, which allows attackers to inject malicious SQL payloads for direct execution. This issue is fixed in version 3.5.5.

## References
- https://github.com/LabRedesCefetRJ/WeGIA/releases/tag/3.5.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67501.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-hj2x-qfm3-2869
- https://nvd.nist.gov/vuln/detail/CVE-2025-67501
- https://github.com/LabRedesCefetRJ/WeGIA/commit/f04b91f584a38c2061a071b26219dba3f25819e6
