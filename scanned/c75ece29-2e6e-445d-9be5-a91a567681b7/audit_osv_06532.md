# [M] BIT-mariadb-2023-52968

## Summary
Severity: Medium
Advisory: BIT-mariadb-2023-52968
Aliases: BIT-mariadb-min-2023-52968, BIT-mysql-client-2023-52968, CVE-2023-52968
Ecosystem: Bitnami
Published: 2025-03-13
Source: https://osv.dev/vulnerability/BIT-mariadb-2023-52968
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.1.0 <11.1.4

## Details
MariaDB Server 10.4 before 10.4.33, 10.5 before 10.5.24, 10.6 before 10.6.17, 10.7 through 10.11 before 10.11.7, 11.0 before 11.0.5, and 11.1 before 11.1.4 calls fix_fields_if_needed under mysql_derived_prepare when derived is not yet prepared, leading to a find_field_in_table crash.

## References
- https://jira.mariadb.org/browse/MDEV-32082
- https://nvd.nist.gov/vuln/detail/CVE-2023-52968
