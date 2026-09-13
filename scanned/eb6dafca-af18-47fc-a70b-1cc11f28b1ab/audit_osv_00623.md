# [M] ALPINE-CVE-2017-3238

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-3238
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3238
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
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Optimizer). Supported versions that are affected are 5.5.53 and earlier, 5.6.34 and earlier and 5.7.16 and earlier. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS v3.0 Base Score 6.5 (Availability impacts).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3238
