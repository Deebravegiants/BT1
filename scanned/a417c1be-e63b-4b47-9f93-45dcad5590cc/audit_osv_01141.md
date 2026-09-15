# [H] ALPINE-CVE-2018-25032

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-25032
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-25032
Type: osv

## Affected
- Alpine:v3.13: `mariadb` — affected >=10.3.0 <10.5.17-r0
- Alpine:v3.14: `mariadb` — affected >=10.3.0 <10.5.17-r0
- Alpine:v3.15: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.16: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.17: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.18: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.19: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.20: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.21: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.22: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.23: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.24: `mariadb` — affected >=10.3.0 <10.6.9-r0
- Alpine:v3.12: `zlib` — affected >=1.2.2.2 <1.2.12-r0
- Alpine:v3.13: `zlib` — affected >=1.2.2.2 <1.2.12-r0
- Alpine:v3.14: `zlib` — affected >=1.2.2.2 <1.2.12-r0
- Alpine:v3.15: `zlib` — affected >=1.2.2.2 <1.2.12-r0
- Alpine:v3.16: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.17: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.18: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.19: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.20: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.21: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.22: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.23: `zlib` — affected >=1.2.2.2 <1.2.11-r4
- Alpine:v3.24: `zlib` — affected >=1.2.2.2 <1.2.11-r4

## Details
zlib before 1.2.12 allows memory corruption when deflating (i.e., when compressing) if the input has many distant matches.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-25032
