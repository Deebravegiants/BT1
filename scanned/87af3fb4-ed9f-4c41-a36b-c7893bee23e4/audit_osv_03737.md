# [C] ALPINE-CVE-2026-44172

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-44172
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44172
Type: osv

## Affected
- Alpine:v3.20: `mariadb` — affected >=0 <10.11.17-r0
- Alpine:v3.21: `mariadb` — affected >=0 <11.4.11-r0
- Alpine:v3.22: `mariadb` — affected >=0 <11.4.11-r0
- Alpine:v3.23: `mariadb` — affected >=0 <11.4.11-r0
- Alpine:v3.24: `mariadb` — affected >=0 <11.8.7-r0

## Details
MariaDB server is a community developed fork of MySQL server. In versions 3.3.18 and 3.4.8, an application that was taking non-validated user input, escaping it with mysql_real_escape_string() and sending it to the database using text protocol and big5 character set was vulnerable to SQL injections, even though mysql_real_escape_string() was supposed to prevent them. This issue has been patched in versions 3.3.19 and 3.4.9.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44172
