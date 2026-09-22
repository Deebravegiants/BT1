# [M] BIT-mariadb-2023-22084

## Summary
Severity: Medium
Advisory: BIT-mariadb-2023-22084
Aliases: BIT-mariadb-min-2023-22084, BIT-mysql-client-2023-22084, CVE-2023-22084
Ecosystem: Bitnami
Published: 2024-10-05
Source: https://osv.dev/vulnerability/BIT-mariadb-2023-22084
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.2.0 <11.2.2

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB).  Supported versions that are affected are 5.7.43 and prior, 8.0.34 and prior and  8.1.0. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server.  Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OR7GNQAJZ7NMHT4HRDNROR3DS272KKET/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UCGSAQFWYIJRIYLZLHPS3MRUS4AQ5JQH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YZL2AT2ZUKB6K22UTISHEZ4JKG4VZ3VO/
- https://security.netapp.com/advisory/ntap-20231027-0009/
- https://www.oracle.com/security-alerts/cpuoct2023.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-22084
- https://mariadb.com/kb/en/security/
