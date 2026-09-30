# [C] WeGIA has Authenticated Time-Based Blind SQL Injection in `restaurar_produto.php` via `id_produto` parameter

## Summary
Severity: Critical
Advisory: CVE-2026-33134
Aliases: GHSA-qg95-x997-66wq
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33134
Type: osv

## Details
WeGIA is a web manager for charitable institutions. Versions 3.6.5 and below contain an authenticated SQL Injection vulnerability in the html/matPat/restaurar_produto.php endpoint. The vulnerability allows an authenticated attacker to inject arbitrary SQL commands via the id_produto GET parameter, leading to full database compromise. In the script /html/matPat/restaurar_produto.php, the application retrieves the id_produto parameter directly from the $_GET global array and interpolates it directly into two SQL query strings without any sanitization, type-casting (e.g., (int)), or using parameterized (prepare/execute) statements. This issue has been fixed in version 3.6.6.

## References
- https://github.com/LabRedesCefetRJ/WeGIA/releases/tag/3.6.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33134.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-qg95-x997-66wq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33134
- https://github.com/LabRedesCefetRJ/WeGIA/pull/1457
