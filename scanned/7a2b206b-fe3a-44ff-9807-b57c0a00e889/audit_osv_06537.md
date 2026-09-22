# [M] BIT-mariadb-2025-21490

## Summary
Severity: Medium
Advisory: BIT-mariadb-2025-21490
Aliases: BIT-mariadb-min-2025-21490, BIT-mysql-client-2025-21490, CVE-2025-21490
Ecosystem: Bitnami
Published: 2025-03-13
Source: https://osv.dev/vulnerability/BIT-mariadb-2025-21490
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.5.0 <11.7.2

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB).  Supported versions that are affected are 8.0.40 and prior, 8.4.3 and prior and  9.1.0 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://www.oracle.com/security-alerts/cpujan2025.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00000.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-21490
- https://security.netapp.com/advisory/ntap-20250131-0004/
