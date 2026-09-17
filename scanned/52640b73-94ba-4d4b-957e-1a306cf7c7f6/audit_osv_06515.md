# [H] BIT-mariadb-2022-27458

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27458
Aliases: BIT-mysql-client-2022-27458, CVE-2022-27458
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27458
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB Server v10.6.3 and below was discovered to contain an use-after-free in the component Binary_string::free_buffer() at /sql/sql_string.h.

## References
- https://jira.mariadb.org/browse/MDEV-28099
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220526-0007/
