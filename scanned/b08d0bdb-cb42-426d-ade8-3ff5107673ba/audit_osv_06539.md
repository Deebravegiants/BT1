# [M] BIT-mariadb-2025-30722

## Summary
Severity: Medium
Advisory: BIT-mariadb-2025-30722
Aliases: BIT-mariadb-min-2025-30722, BIT-mysql-client-2025-30722, CVE-2025-30722
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-mariadb-2025-30722
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.5.0 <11.8.2

## Details
Vulnerability in the MySQL Client product of Oracle MySQL (component: Client: mysqldump).  Supported versions that are affected are 8.0.0-8.0.41, 8.4.0-8.4.4 and  9.0.0-9.2.0. Difficult to exploit vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Client.  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all MySQL Client accessible data as well as  unauthorized update, insert or delete access to some of MySQL Client accessible data. CVSS 3.1 Base Score 5.9 (Confidentiality and Integrity impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30722
- https://security.netapp.com/advisory/ntap-20250418-0005/
- https://www.oracle.com/security-alerts/cpuapr2025.html
- https://lists.debian.org/debian-lts-announce/2025/06/msg00005.html
