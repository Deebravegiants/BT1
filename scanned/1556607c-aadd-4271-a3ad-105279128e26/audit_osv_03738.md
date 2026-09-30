# [M] ALPINE-CVE-2026-44173

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-44173
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44173
Type: osv

## Affected
- Alpine:v3.20: `mariadb` — affected >=10.6.1 <10.11.17-r0
- Alpine:v3.21: `mariadb` — affected >=10.6.1 <11.4.11-r0
- Alpine:v3.22: `mariadb` — affected >=10.6.1 <11.4.11-r0
- Alpine:v3.23: `mariadb` — affected >=10.6.1 <11.4.11-r0
- Alpine:v3.24: `mariadb` — affected >=10.6.1 <11.8.7-r0

## Details
MariaDB server is a community developed fork of MySQL server. From versions 10.6.1 to before 10.6.26, 10.11.1 to before 10.11.17, 11.4.1 to before 11.4.11, 11.8.1 to before 11.8.7, and 12.3.1, MariaDB allowed SELECT ... INTO OUTFILE and SELECT ... INTO DUMPFILE without verifying the FILE privilege if the FROM clause contained only subqueries. This issue has been patched in versions 10.6.26, 10.11.17, 11.4.11, 11.8.7, and 12.3.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44173
