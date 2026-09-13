# [H] Chamilo LMS: SQL Injection in the statistics AJAX endpoint

## Summary
Severity: High
Advisory: CVE-2026-30881
Aliases: GHSA-5ggx-x2cv-4h44
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2026-30881
Type: osv

## Details
Chamilo LMS is a learning management system. Version 1.11.34 and prior contains a SQL Injection vulnerability in the statistics AJAX endpoint. The parameters date_start and date_end from $_REQUEST are embedded directly into a raw SQL string without proper sanitization. Although Database::escape_string() is called downstream, its output is immediately neutralized by str_replace("\'", "'", ...), which restores any injected single quotes — effectively bypassing the escaping mechanism entirely. This allows an authenticated attacker to inject arbitrary SQL statements into the database query, enabling blind time-based and conditional data extraction. This issue has been patched in version 1.11.36.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30881.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-5ggx-x2cv-4h44
- https://nvd.nist.gov/vuln/detail/CVE-2026-30881
