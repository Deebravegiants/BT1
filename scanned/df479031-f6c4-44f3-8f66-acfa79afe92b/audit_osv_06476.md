# [M] BIT-mariadb-2021-2154

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-2154
Aliases: BIT-mariadb-min-2021-2154, BIT-mysql-client-2021-2154, CVE-2021-2154
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-2154
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0 <10.5.10

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: DML). Supported versions that are affected are 5.7.33 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DPA3CTGXPVWKHMCQDVURK4ETH7GE34KK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GAU7KW36A6TQGKG3RUITYSVUFIHBY3OT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PEF5CRATUGQZUSQU63MHQIDZPOLHW2VE/
- https://security.gentoo.org/glsa/202105-27
- https://security.gentoo.org/glsa/202105-28
- https://security.netapp.com/advisory/ntap-20210513-0002/
- https://www.oracle.com/security-alerts/cpuapr2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-2154
