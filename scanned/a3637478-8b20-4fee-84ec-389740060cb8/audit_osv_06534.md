# [M] BIT-mariadb-2023-52970

## Summary
Severity: Medium
Advisory: BIT-mariadb-2023-52970
Aliases: BIT-mariadb-min-2023-52970, BIT-mysql-client-2023-52970, CVE-2023-52970
Ecosystem: Bitnami
Published: 2025-03-13
Source: https://osv.dev/vulnerability/BIT-mariadb-2023-52970
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.5.0 <11.8.2

## Details
MariaDB Server 10.4 through 10.5.*, 10.6 through 10.6.*, 10.7 through 10.11.*, 11.0 through 11.0.*, and 11.1 through 11.4.* crashes in Item_direct_view_ref::derived_field_transformer_for_where.

## References
- https://jira.mariadb.org/browse/MDEV-32086
- https://nvd.nist.gov/vuln/detail/CVE-2023-52970
- https://lists.debian.org/debian-lts-announce/2025/05/msg00006.html
