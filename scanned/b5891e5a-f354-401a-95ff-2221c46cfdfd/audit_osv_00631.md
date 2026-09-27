# [H] ALPINE-CVE-2017-3308

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-3308
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3308
Type: osv

## Affected
- Alpine:v3.3: `mariadb` — affected >=5.5.0 <10.1.23-r0
- Alpine:v3.4: `mariadb` — affected >=5.5.0 <10.1.23-r0
- Alpine:v3.5: `mariadb` — affected >=5.5.0 <10.1.23-r0
- Alpine:v3.6: `mariadb` — affected >=5.5.0 <10.1.23-r0

## Details
Vulnerability in the MySQL Server component of Oracle MySQL (subcomponent: Server: DML). Supported versions that are affected are 5.5.54 and earlier, 5.6.35 and earlier and 5.7.17 and earlier. Easily "exploitable" vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server. While the vulnerability is in MySQL Server, attacks may significantly impact additional products. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.0 Base Score 7.7 (Availability impacts). CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3308
