# [H] BIT-mariadb-2022-27447

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27447
Aliases: BIT-mariadb-min-2022-27447, BIT-mysql-client-2022-27447, CVE-2022-27447
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27447
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB Server v10.9 and below was discovered to contain a use-after-free via the component Binary_string::free_buffer() at /sql/sql_string.h.

## References
- https://jira.mariadb.org/browse/MDEV-28099
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220526-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27447
