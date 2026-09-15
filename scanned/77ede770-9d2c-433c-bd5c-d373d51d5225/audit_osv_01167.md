# [M] ALPINE-CVE-2018-3081

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-3081
Ecosystem: Alpine:v3.6, Alpine:v3.7
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H)
Published: 2018-07-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-3081
Type: osv

## Affected
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.37-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.37-r0

## Details
Vulnerability in the MySQL Client component of Oracle MySQL (subcomponent: Client programs). Supported versions that are affected are 5.5.60 and prior, 5.6.40 and prior, 5.7.22 and prior and 8.0.11 and prior. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Client. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Client as well as unauthorized update, insert or delete access to some of MySQL Client accessible data. CVSS 3.0 Base Score 5.0 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-3081
