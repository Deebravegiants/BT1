# [C] SPIP < 4.4.10 SQL Injection RCE via Union & PHP Tags

## Summary
Severity: Critical
Advisory: CVE-2026-22206
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-22206
Type: osv

## Details
SPIP versions prior to 4.4.10 contain a SQL injection vulnerability that allows authenticated low-privilege users to execute arbitrary SQL queries by manipulating union-based injection techniques. Attackers can exploit this SQL injection flaw combined with PHP tag processing to achieve remote code execution on the server.

## References
- https://git.spip.net/spip/spip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22206.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22206
- https://www.vulncheck.com/advisories/spip-sql-injection-rce-via-union-php-tags
- https://blog.spip.net/Mise-a-jour-de-securite-sortie-de-SPIP-4-4-10.html
