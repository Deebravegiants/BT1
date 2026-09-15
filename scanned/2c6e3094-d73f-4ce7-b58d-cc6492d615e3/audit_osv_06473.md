# [M] BIT-mariadb-2021-2022

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-2022
Aliases: BIT-mariadb-min-2021-2022, BIT-mysql-client-2021-2022, CVE-2021-2022
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-2022
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0 <10.5.5

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB). Supported versions that are affected are 5.6.50 and prior, 5.7.32 and prior and 8.0.22 and prior. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.4 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CS5THZSGI7O2CZO44NWYE57AG2T7NK3K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T7EAHJPWOOF4D6PEFLXW5IQWRRSZ3HRC/
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20210219-0003/
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-2022
