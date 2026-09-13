# [M] BIT-mariadb-2021-2011

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-2011
Aliases: BIT-mariadb-min-2021-2011, BIT-mysql-client-2021-2011, CVE-2021-2011
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-2011
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.2.0 <10.2.15

## Details
Vulnerability in the MySQL Client product of Oracle MySQL (component: C API). Supported versions that are affected are 5.7.32 and prior and 8.0.22 and prior. Difficult to exploit vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise MySQL Client. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Client. CVSS 3.1 Base Score 5.9 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CS5THZSGI7O2CZO44NWYE57AG2T7NK3K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T7EAHJPWOOF4D6PEFLXW5IQWRRSZ3HRC/
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20210622-0001/
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-2011
