# [H] BIT-mariadb-2022-27384

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27384
Aliases: BIT-mariadb-min-2022-27384, BIT-mysql-client-2022-27384, CVE-2022-27384
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27384
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.8.0 <10.8.3

## Details
An issue in the component Item_subselect::init_expr_cache_tracker of MariaDB Server v10.6 and below was discovered to allow attackers to cause a Denial of Service (DoS) via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26047
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220519-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27384
