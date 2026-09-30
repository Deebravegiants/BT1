# [M] ALPINE-CVE-2022-21427

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-21427
Ecosystem: Alpine:v3.12
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-21427
Type: osv

## Affected
- Alpine:v3.12: `mariadb` — affected >=10.2.0 <10.4.25-r0

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: FTS). Supported versions that are affected are 5.7.37 and prior and 8.0.28 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://security.alpinelinux.org/vuln/CVE-2022-21427
