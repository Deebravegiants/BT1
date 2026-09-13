# [H] ALPINE-CVE-2018-2562

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-2562
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-01-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-2562
Type: osv

## Affected
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.32-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server : Partition). Supported versions that are affected are 5.5.58 and prior, 5.6.38 and prior and 5.7.19 and prior. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server as well as unauthorized update, insert or delete access to some of MySQL Server accessible data. CVSS 3.0 Base Score 7.1 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-2562
