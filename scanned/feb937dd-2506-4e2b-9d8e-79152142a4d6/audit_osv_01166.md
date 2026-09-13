# [H] ALPINE-CVE-2018-3064

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-3064
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-07-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-3064
Type: osv

## Affected
- Alpine:v3.6: `mariadb` — affected >=10.0.0 <10.1.37-r0
- Alpine:v3.7: `mariadb` — affected >=10.0.0 <10.1.37-r0
- Alpine:v3.8: `mariadb` — affected >=10.0.0 <10.2.19-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: InnoDB). Supported versions that are affected are 5.6.40 and prior, 5.7.22 and prior and 8.0.11 and prior. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 7.1 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-3064
