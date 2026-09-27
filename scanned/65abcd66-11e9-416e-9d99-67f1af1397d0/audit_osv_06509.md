# [H] BIT-mariadb-2022-27387

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27387
Aliases: BIT-mariadb-min-2022-27387, BIT-mysql-client-2022-27387, CVE-2022-27387
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27387
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB Server v10.7 and below was discovered to contain a global buffer overflow in the component decimal_bin_size, which is exploited via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26422
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220526-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27387
