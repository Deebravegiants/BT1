# [M] BIT-mariadb-2021-2180

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-2180
Aliases: BIT-mariadb-min-2021-2180, BIT-mysql-client-2021-2180, CVE-2021-2180
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-2180
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.2.0 <10.2.38

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: InnoDB). Supported versions that are affected are 5.7.33 and prior and 8.0.23 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AKV7TRUEQW6EV45RSZVVFLVQMNHVHBCJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JJQRPXNDH6YHQLUSCS5VA7DAW32PN7N7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UJVUTKKFQAWR7NURCQHQQ5JHTVYGEOYQ/
- https://security.gentoo.org/glsa/202105-27
- https://security.gentoo.org/glsa/202105-28
- https://security.netapp.com/advisory/ntap-20210513-0002/
- https://www.oracle.com/security-alerts/cpuapr2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-2180
