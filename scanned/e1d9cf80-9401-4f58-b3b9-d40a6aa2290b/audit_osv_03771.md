# [H] ALPINE-CVE-2026-48165

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-48165
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-48165
Type: osv

## Affected
- Alpine:v3.20: `mariadb` — affected >=10.6.1 <10.11.18-r0
- Alpine:v3.21: `mariadb` — affected >=10.6.1 <11.4.12-r0
- Alpine:v3.22: `mariadb` — affected >=10.6.1 <11.4.12-r0
- Alpine:v3.23: `mariadb` — affected >=10.6.1 <11.4.12-r0
- Alpine:v3.24: `mariadb` — affected >=10.6.1 <11.8.8-r0

## Details
MariaDB server is a community developed fork of MySQL server. From versions 10.6.1 to before 10.6.27, 10.11.1 to before 10.11.18, 11.4.1 to before 11.4.12, 11.8.1 to before 11.8.8, and 12.3.1, a high-privileged MariaDB user could've used wsrep_sst_receive_address or wsrep_sst_donor global system variables to execute shell commands as the uid of the mariadbd process on the galera joiner node. This issue has been patched in versions 10.6.27, 10.11.18, 11.4.12, 11.8.8, and 12.3.2.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-48165
