# [H] ALPINE-CVE-2018-2755

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-2755
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-2755
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.11: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.12: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.13: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.14: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.15: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.16: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.17: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.18: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.19: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.20: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.21: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.22: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.23: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.24: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.37-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.37-r0
- Alpine:v3.8: `mariadb` — affected >=5.5.0 <10.2.15-r0
- Alpine:v3.9: `mariadb` — affected >=5.5.0 <10.2.15-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Replication). Supported versions that are affected are 5.5.59 and prior, 5.6.39 and prior and 5.7.21 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in takeover of MySQL Server. CVSS 3.0 Base Score 7.7 (Confidentiality, Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-2755
