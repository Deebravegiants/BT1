# [M] ALPINE-CVE-2021-2389

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-2389
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-2389
Type: osv

## Affected
- Alpine:v3.11: `mariadb` — affected >=10.2.0 <10.4.21-r0
- Alpine:v3.12: `mariadb` — affected >=10.2.0 <10.4.21-r0
- Alpine:v3.13: `mariadb` — affected >=10.2.0 <10.5.12-r0
- Alpine:v3.14: `mariadb` — affected >=10.2.0 <10.5.12-r0
- Alpine:v3.15: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.16: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.17: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.18: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.19: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.20: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.21: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.22: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.23: `mariadb` — affected >=10.2.0 <10.6.4-r0
- Alpine:v3.24: `mariadb` — affected >=10.2.0 <10.6.4-r0

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB). Supported versions that are affected are 5.7.34 and prior and 8.0.25 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 5.9 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2021-2389
