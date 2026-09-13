# [H] BIT-mariadb-2022-27383

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27383
Aliases: BIT-mariadb-min-2022-27383, BIT-mysql-client-2022-27383, CVE-2022-27383
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27383
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.8.0 <10.8.3

## Details
MariaDB Server v10.6 and below was discovered to contain an use-after-free in the component my_strcasecmp_8bit, which is exploited via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26323
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220519-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27383
