# [M] ALPINE-CVE-2018-3174

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-3174
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-3174
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.11: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.12: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.13: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.14: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.15: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.16: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.17: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.18: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.19: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.20: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.21: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.22: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.23: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.24: `mariadb` — affected >=5.5.0 <10.3.11-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.37-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.37-r0
- Alpine:v3.8: `mariadb` — affected >=5.5.0 <10.2.19-r0
- Alpine:v3.9: `mariadb` — affected >=5.5.0 <10.3.11-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Client programs). Supported versions that are affected are 5.5.61 and prior, 5.6.41 and prior, 5.7.23 and prior and 8.0.12 and prior. Difficult to exploit vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. While the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.0 Base Score 5.3 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:H/PR:H/UI:N/S:C/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-3174
