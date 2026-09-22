# [M] BIT-mariadb-2023-52969

## Summary
Severity: Medium
Advisory: BIT-mariadb-2023-52969
Aliases: BIT-mariadb-min-2023-52969, BIT-mysql-client-2023-52969, CVE-2023-52969
Ecosystem: Bitnami
Published: 2025-03-13
Source: https://osv.dev/vulnerability/BIT-mariadb-2023-52969
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.5.0 <11.8.2

## Details
MariaDB Server 10.4 through 10.5.*, 10.6 through 10.6.*, 10.7 through 10.11.*, and 11.0 through 11.0.* can sometimes crash with an empty backtrace log. This may be related to make_aggr_tables_info and optimize_stage2.

## References
- https://jira.mariadb.org/browse/MDEV-32083
- https://nvd.nist.gov/vuln/detail/CVE-2023-52969
- https://lists.debian.org/debian-lts-announce/2025/05/msg00006.html
