# [M] BIT-mariadb-2021-46658

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-46658
Aliases: BIT-mariadb-min-2021-46658, BIT-mysql-client-2021-46658, CVE-2021-46658
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-46658
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.3

## Details
save_window_function_values in MariaDB before 10.6.3 allows an application crash because of incorrect handling of with_window_func=true for a subquery.

## References
- https://jira.mariadb.org/browse/MDEV-25630
- https://mariadb.com/kb/en/security/
- https://security.netapp.com/advisory/ntap-20220221-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2021-46658
