# [M] ALPINE-CVE-2019-2739

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-2739
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.1 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-2739
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=5.5.0 <10.3.17-r0
- Alpine:v3.11: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.12: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.13: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.14: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.15: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.16: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.17: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.18: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.19: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.20: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.21: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.22: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.23: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.24: `mariadb` — affected >=5.5.0 <10.4.7-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.41-r0
- Alpine:v3.8: `mariadb` — affected >=5.5.0 <10.2.26-r0
- Alpine:v3.9: `mariadb` — affected >=5.5.0 <10.3.17-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Security: Privileges). Supported versions that are affected are 5.6.44 and prior, 5.7.26 and prior and 8.0.16 and prior. Easily exploitable vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 5.1 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-2739
