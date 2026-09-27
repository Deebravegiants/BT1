# [M] BIT-mariadb-2021-46666

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-46666
Aliases: BIT-mariadb-min-2021-46666, BIT-mysql-client-2021-46666, CVE-2021-46666
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-46666
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.2

## Details
MariaDB before 10.6.2 allows an application crash because of mishandling of a pushdown from a HAVING clause to a WHERE clause.

## References
- https://jira.mariadb.org/browse/MDEV-25635
- https://mariadb.com/kb/en/security/
- https://security.netapp.com/advisory/ntap-20220221-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2021-46666
