# [H] BIT-mariadb-2022-27377

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27377
Aliases: BIT-mariadb-min-2022-27377, BIT-mysql-client-2022-27377, CVE-2022-27377
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27377
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB Server v10.6.3 and below was discovered to contain an use-after-free in the component Item_func_in::cleanup(), which is exploited via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26281
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220526-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27377
