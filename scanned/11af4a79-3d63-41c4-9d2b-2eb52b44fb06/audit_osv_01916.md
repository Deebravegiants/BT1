# [M] ALPINE-CVE-2020-2752

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-2752
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-2752
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=5.5.0 <10.3.23-r0
- Alpine:v3.11: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.12: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.13: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.14: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.15: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.16: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.17: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.18: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.19: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.20: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.21: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.22: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.23: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.24: `mariadb` — affected >=5.5.0 <10.4.13-r0
- Alpine:v3.8: `mariadb` — affected >=5.5.0 <10.2.32-r0
- Alpine:v3.9: `mariadb` — affected >=5.5.0 <10.3.23-r0

## Details
Vulnerability in the MySQL Client product of Oracle MySQL (component: C API). Supported versions that are affected are 5.6.47 and prior, 5.7.27 and prior and 8.0.17 and prior. Difficult to exploit vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Client. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Client. CVSS 3.0 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-2752
