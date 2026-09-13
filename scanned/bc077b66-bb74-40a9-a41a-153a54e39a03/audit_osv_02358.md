# [M] ALPINE-CVE-2021-46668

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-46668
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-46668
Type: osv

## Affected
- Alpine:v3.12: `mariadb` — affected >=10.2.0 <10.4.24-r0
- Alpine:v3.13: `mariadb` — affected >=10.2.0 <10.5.15-r0
- Alpine:v3.14: `mariadb` — affected >=10.2.0 <10.5.15-r0
- Alpine:v3.15: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.16: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.17: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.18: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.19: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.20: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.21: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.22: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.23: `mariadb` — affected >=10.2.0 <10.6.7-r0
- Alpine:v3.24: `mariadb` — affected >=10.2.0 <10.6.7-r0

## Details
MariaDB through 10.5.9 allows an application crash via certain long SELECT DISTINCT statements that improperly interact with storage-engine resource limitations for temporary data structures.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-46668
