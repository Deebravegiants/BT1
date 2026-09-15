# [H] BIT-mariadb-2022-27379

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27379
Aliases: BIT-mariadb-min-2022-27379, BIT-mysql-client-2022-27379, CVE-2022-27379
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27379
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
An issue in the component Arg_comparator::compare_real_fixed of MariaDB Server v10.6.2 and below was discovered to allow attackers to cause a Denial of Service (DoS) via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26353
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220526-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27379
