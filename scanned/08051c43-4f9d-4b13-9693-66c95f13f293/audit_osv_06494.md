# [M] BIT-mariadb-2022-21595

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-21595
Aliases: BIT-mariadb-min-2022-21595, BIT-mysql-client-2022-21595, CVE-2022-21595
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-21595
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.2

## Details
Vulnerability in the MySQL Server product of Oracle MySQL (component: C API). Supported versions that are affected are 5.7.36 and prior and 8.0.27 and prior. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Server. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Server. CVSS 3.1 Base Score 4.4 (Availability impacts). CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H).

## References
- https://security.netapp.com/advisory/ntap-20221028-0013/
- https://www.oracle.com/security-alerts/cpuoct2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-21595
- https://mariadb.com/kb/en/security/
