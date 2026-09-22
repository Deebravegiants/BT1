# [H] CVE-2026-46446

## Summary
Severity: High
Advisory: CVE-2026-46446
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-46446
Type: osv

## Details
SOGo before 5.12.7, when PostgreSQL or MariaDB is used, and cleartext passwords are stored, allows SQL injection. This is related to c_password = '%@' in changePasswordForLogin.

## References
- https://github.com/Alinto/sogo/pull/379/changes/1f7e5d2b2c2047c44a6a9e05f73c36491cb96d21
- https://www.mail-archive.com/debian-bugs-dist%40lists.debian.org/msg2100131.html
- https://www.sogo.nu/news/2026/sogo-v5127-released.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46446
