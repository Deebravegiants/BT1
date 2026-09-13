# [M] BIT-mariadb-2022-21427

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-21427
Aliases: BIT-mariadb-min-2022-21427, BIT-mysql-client-2022-21427, CVE-2022-21427
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-21427
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0 <10.5.7

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: FTS). Supported versions that are affected are 5.7.37 and prior and 8.0.28 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220429-0005/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-21427
- https://mariadb.com/kb/en/security/
