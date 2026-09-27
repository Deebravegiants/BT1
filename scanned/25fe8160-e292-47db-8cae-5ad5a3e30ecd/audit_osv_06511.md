# [H] BIT-mariadb-2022-27448

## Summary
Severity: High
Advisory: BIT-mariadb-2022-27448
Aliases: BIT-mariadb-min-2022-27448, BIT-mysql-client-2022-27448, CVE-2022-27448
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-27448
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
There is an Assertion failure in MariaDB Server v10.9 and below via 'node->pcur->rel_pos == BTR_PCUR_ON' at /row/row0mysql.cc.

## References
- https://jira.mariadb.org/browse/MDEV-28095
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220526-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2022-27448
