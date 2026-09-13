# [M] ALPINE-CVE-2017-10378

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-10378
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-10378
Type: osv

## Affected
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.32-r0
- Alpine:v3.7: `mariadb` — affected >=5.5.0 <10.1.32-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: Optimizer). Supported versions that are affected are 5.5.57 and earlier, 5.6.37 and earlier and 5.7.11 and earlier. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.0 Base Score 6.5 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-10378
