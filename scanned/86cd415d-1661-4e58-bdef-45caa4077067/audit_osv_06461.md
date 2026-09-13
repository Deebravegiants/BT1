# [M] BIT-mariadb-2020-14789

## Summary
Severity: Medium
Advisory: BIT-mariadb-2020-14789
Aliases: BIT-mariadb-min-2020-14789, BIT-mysql-client-2020-14789, CVE-2020-14789
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2020-14789
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0 <10.5.7

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: FTS). Supported versions that are affected are 5.7.31 and prior and 8.0.21 and prior. Easily exploitable vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.9 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GZU3PA5XJXNQ4C4F6435ARM6WKM3OZYR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JBZZ3XIRPFPAWBZLYBN777ANXSFXAPPB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O7RVY2Z7HYQHFJXBGARXUAGKUDAWYPP4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OPW5YMZR5C7D7NBZQSTDOB3XAI5QP32Y/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X4X2BMF3EILMTXGOZDTPYS3KT5VWLA2P/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZVS6KNVBZCLZBKNJ5JA2PGAG3NTOJVH6/
- https://security.gentoo.org/glsa/202105-27
- https://security.netapp.com/advisory/ntap-20201023-0003/
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-14789
