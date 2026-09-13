# [H] SQL Injection in LMS

## Summary
Severity: High
Advisory: CVE-2026-40455
CVSS: 7.5 (CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-40455
Type: osv

## Details
An SQL Injection vulnerability exists in LMS (LAN Management System) before commit 4cb30a7 within the "tarifflist.php" module due to insufficient sanitization of the POST "tg[]" parameter. The application directly concatenates user-supplied array values into an SQL query using "implode()", allowing authenticated attackers to perform Error-Based SQL injection and extract sensitive database information.

## References
- https://lms.org.pl/
- https://cert.pl/posts/2026/06/CVE-2026-40455
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40455.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40455
- https://github.com/chilek/lms/commit/4cb30a70e7e3d8a0ea53afa2dbef19d5243d449b
- https://github.com/chilek/lms
