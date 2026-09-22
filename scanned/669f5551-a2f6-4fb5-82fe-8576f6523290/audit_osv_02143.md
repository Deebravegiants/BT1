# [H] ALPINE-CVE-2021-27928

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-27928
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-27928
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=10.2 <10.3.28-r0
- Alpine:v3.11: `mariadb` — affected >=10.2 <10.4.18-r0
- Alpine:v3.12: `mariadb` — affected >=10.2 <10.4.18-r0
- Alpine:v3.13: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.14: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.15: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.16: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.17: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.18: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.19: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.20: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.21: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.22: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.23: `mariadb` — affected >=10.2 <10.5.9-r0
- Alpine:v3.24: `mariadb` — affected >=10.2 <10.5.9-r0

## Details
A remote code execution issue was discovered in MariaDB 10.2 before 10.2.37, 10.3 before 10.3.28, 10.4 before 10.4.18, and 10.5 before 10.5.9; Percona Server through 2021-03-03; and the wsrep patch through 2021-03-03 for MySQL. An untrusted search path leads to eval injection, in which a database SUPER user can execute OS commands after modifying wsrep_provider and wsrep_notify_cmd. NOTE: this does not affect an Oracle product.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-27928
