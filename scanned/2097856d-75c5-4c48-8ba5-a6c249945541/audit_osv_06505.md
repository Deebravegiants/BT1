# [H] BIT-mariadb-2022-27382

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27382
Aliases: BIT-mariadb-min-2022-27382, BIT-mysql-client-2022-27382, CVE-2022-27382
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27382
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB Server v10.7 and below was discovered to contain a segmentation fault via the component Item_field::used_tables/update_depend_map_for_order.

## References
- https://jira.mariadb.org/browse/MDEV-26402
- https://security.netapp.com/advisory/ntap-20220526-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27382
