# [H] ALPINE-CVE-2022-27387

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-27387
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-27387
Type: osv

## Affected
- Alpine:v3.12: `mariadb` — affected >=10.2.0 <10.4.25-r0
- Alpine:v3.13: `mariadb` — affected >=10.2.0 <10.5.16-r0
- Alpine:v3.14: `mariadb` — affected >=10.2.0 <10.5.16-r0
- Alpine:v3.15: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.16: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.17: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.18: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.19: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.20: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.21: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.22: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.23: `mariadb` — affected >=10.2.0 <10.6.8-r0
- Alpine:v3.24: `mariadb` — affected >=10.2.0 <10.6.8-r0

## Details
MariaDB Server v10.7 and below was discovered to contain a global buffer overflow in the component decimal_bin_size, which is exploited via specially crafted SQL statements.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-27387
