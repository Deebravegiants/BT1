# [H] BIT-mariadb-2022-32083

## Summary
Severity: High
Advisory: BIT-mariadb-2022-32083
Aliases: BIT-mariadb-min-2022-32083, BIT-mysql-client-2022-32083, CVE-2022-32083
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-32083
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB v10.2 to v10.6.1 was discovered to contain a segmentation fault via the component Item_subselect::init_expr_cache_tracker.

## References
- https://jira.mariadb.org/browse/MDEV-26047
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220826-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2022-32083
