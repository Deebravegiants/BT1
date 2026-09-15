# [H] ALPINE-CVE-2022-27385

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-27385
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27385
Type: osv

## Affected
- Alpine:v3.16: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.17: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.18: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.19: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.20: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.21: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.22: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.23: `mariadb` — affected >=10.4.0 <10.6.7-r0
- Alpine:v3.24: `mariadb` — affected >=10.4.0 <10.6.7-r0

## Details
An issue in the component Used_tables_and_const_cache::used_tables_and_const_cache_join of MariaDB Server v10.7 and below was discovered to allow attackers to cause a Denial of Service (DoS) via specially crafted SQL statements.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27385
