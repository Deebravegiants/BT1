# [M] ALPINE-CVE-2025-21490

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-21490
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-21490
Type: osv

## Affected
- Alpine:v3.18: `mariadb` — affected >=0 <10.11.11-r0
- Alpine:v3.19: `mariadb` — affected >=0 <10.11.11-r0
- Alpine:v3.20: `mariadb` — affected >=0 <10.11.11-r0
- Alpine:v3.21: `mariadb` — affected >=0 <11.4.5-r0
- Alpine:v3.22: `mariadb` — affected >=0 <11.4.5-r0
- Alpine:v3.23: `mariadb` — affected >=0 <11.4.5-r0
- Alpine:v3.24: `mariadb` — affected >=0 <11.4.5-r0

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB).  Supported versions that are affected are 8.0.40 and prior, 8.4.3 and prior and  9.1.0 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2025-21490
