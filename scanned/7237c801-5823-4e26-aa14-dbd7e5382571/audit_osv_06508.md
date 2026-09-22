# [H] BIT-mariadb-2022-27385

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27385
Aliases: BIT-mariadb-min-2022-27385, BIT-mysql-client-2022-27385, CVE-2022-27385
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27385
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.5

## Details
An issue in the component Used_tables_and_const_cache::used_tables_and_const_cache_join of MariaDB Server v10.7 and below was discovered to allow attackers to cause a Denial of Service (DoS) via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26415
- https://security.netapp.com/advisory/ntap-20220526-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27385
