# [M] BIT-mariadb-2024-21096

## Summary
Severity: Medium
Advisory: BIT-mariadb-2024-21096
Aliases: BIT-mariadb-min-2024-21096, BIT-mysql-client-2024-21096, CVE-2024-21096
Ecosystem: Bitnami
Published: 2024-10-05
Source: https://osv.dev/vulnerability/BIT-mariadb-2024-21096
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.3.0 <11.4.2

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Client: mysqldump).  Supported versions that are affected are 8.0.36 and prior and  8.3.0 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with logon to the infrastructure where MySQL Server executes to compromise MySQL Server.  Successful attacks of this vulnerability can result in  unauthorized update, insert or delete access to some of MySQL Server accessible data as well as  unauthorized read access to a subset of MySQL Server accessible data and unauthorized ability to cause a partial denial of service (partial DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Confidentiality, Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L).

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CKWVBZ6DBRFMLDXTHJUZ6LU7MJ5RTNA7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KFYBDWDBE4YICSV34LJZGYRVSG6QIRKE/
- https://security.netapp.com/advisory/ntap-20240426-0013/
- https://www.oracle.com/security-alerts/cpuapr2024.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00034.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-21096
- https://mariadb.com/kb/en/security/
