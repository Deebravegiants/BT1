# [C] OS Command Injection in LMS

## Summary
Severity: Critical
Advisory: CVE-2026-40456
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-40456
Type: osv

## Details
An OS Command Injection vulnerability exists in LMS (LAN Management System) before commit 9fcb4de due to an IP address parameter being passed to the "exec()" function without proper validation, allowing attackers to execute arbitrary operating system commands.

## References
- https://lms.org.pl/
- https://cert.pl/posts/2026/06/CVE-2026-40455
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40456.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40456
- https://github.com/chilek/lms/commit/9fcb4de19b7d76394898dbc124252b86b07ac0ed
- https://github.com/chilek/lms
