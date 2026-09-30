# [M] ALPINE-CVE-2023-22084

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-22084
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-22084
Type: osv

## Affected
- Alpine:v3.16: `mariadb` — affected >=10.4.0 <10.6.16-r0
- Alpine:v3.17: `mariadb` — affected >=10.4.0 <10.6.16-r0
- Alpine:v3.18: `mariadb` — affected >=10.4.0 <10.11.6-r0
- Alpine:v3.19: `mariadb` — affected >=10.4.0 <10.11.6-r0
- Alpine:v3.20: `mariadb` — affected >=10.4.0 <10.11.6-r0
- Alpine:v3.21: `mariadb` — affected >=10.4.0 <10.11.6-r0
- Alpine:v3.22: `mariadb` — affected >=10.4.0 <10.11.6-r0
- Alpine:v3.23: `mariadb` — affected >=10.4.0 <10.11.6-r0
- Alpine:v3.24: `mariadb` — affected >=10.4.0 <10.11.6-r0

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB).  Supported versions that are affected are 5.7.43 and prior, 8.0.34 and prior and  8.1.0. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2023-22084
