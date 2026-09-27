# [H] BIT-mariadb-2022-27457

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27457
Aliases: BIT-mariadb-min-2022-27457, BIT-mysql-client-2022-27457, CVE-2022-27457
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27457
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB Server v10.6.3 and below was discovered to contain an use-after-free in the component my_mb_wc_latin1 at /strings/ctype-latin1.c.

## References
- https://jira.mariadb.org/browse/MDEV-28098
- https://security.netapp.com/advisory/ntap-20220526-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27457
