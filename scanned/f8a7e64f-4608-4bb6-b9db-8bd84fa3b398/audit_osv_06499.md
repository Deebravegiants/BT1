# [H] BIT-mariadb-2022-27376

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27376
Aliases: BIT-mariadb-min-2022-27376, BIT-mysql-client-2022-27376, CVE-2022-27376
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27376
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB Server v10.6.5 and below was discovered to contain an use-after-free in the component Item_args::walk_arg, which is exploited via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26354
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220519-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27376
