# [M] ALPINE-CVE-2018-3060

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-3060
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-07-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-3060
Type: osv

## Affected
- Alpine:v3.6: `mariadb` — affected >=10.2.0 <10.1.37-r0
- Alpine:v3.7: `mariadb` — affected >=10.2.0 <10.1.37-r0
- Alpine:v3.8: `mariadb` — affected >=10.2.0 <10.2.19-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: InnoDB). Supported versions that are affected are 5.7.22 and prior and 8.0.11 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized creation, deletion or modification access to critical data or all MySQL Server accessible data and unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.0 Base Score 6.5 (Integrity and Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2018-3060
