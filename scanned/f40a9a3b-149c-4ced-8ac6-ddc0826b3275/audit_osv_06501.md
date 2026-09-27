# [H] BIT-mariadb-2022-27378

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27378
Aliases: BIT-mariadb-min-2022-27378, BIT-mysql-client-2022-27378, CVE-2022-27378
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27378
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.9.0 <10.9.1

## Details
An issue in the component Create_tmp_table::finalize of MariaDB Server v10.7 and below was discovered to allow attackers to cause a Denial of Service (DoS) via specially crafted SQL statements.

## References
- https://jira.mariadb.org/browse/MDEV-26423
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220526-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27378
