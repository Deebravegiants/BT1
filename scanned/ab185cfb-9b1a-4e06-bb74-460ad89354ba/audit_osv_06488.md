# [M] BIT-mariadb-2021-46662

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-46662
Aliases: BIT-mariadb-min-2021-46662, BIT-mysql-client-2021-46662, CVE-2021-46662
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-46662
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.5

## Details
MariaDB through 10.5.9 allows a set_var.cc application crash via certain uses of an UPDATE statement in conjunction with a nested subquery.

## References
- https://jira.mariadb.org/browse/MDEV-25637
- https://mariadb.com/kb/en/security/
- https://security.netapp.com/advisory/ntap-20220221-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2021-46662
