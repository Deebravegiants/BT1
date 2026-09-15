# [M] ALPINE-CVE-2017-3318

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3318
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3318
Type: osv

## Affected
- Alpine:v3.10: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.11: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.12: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.13: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.14: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.15: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.16: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.17: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.18: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.19: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.2: `mariadb` — affected >=5.5.0 <5.5.54-r0
- Alpine:v3.20: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.21: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.22: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.23: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.24: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.3: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.8: `mariadb` — affected >=5.5.0 <10.1.21-r0
- Alpine:v3.9: `mariadb` — affected >=5.5.0 <10.1.21-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Error Handling). Supported versions that are affected are 5.5.53 and earlier, 5.6.34 and earlier and 5.7.16 and earlier. Difficult to exploit vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server. Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in unauthorized access to critical data or complete access to all MySQL Server accessible data. CVSS v3.0 Base Score 4.0 (Confidentiality impacts).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3318
