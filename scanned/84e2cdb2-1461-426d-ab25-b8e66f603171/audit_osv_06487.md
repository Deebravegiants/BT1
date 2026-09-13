# [M] BIT-mariadb-2021-46661

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-46661
Aliases: BIT-mariadb-min-2021-46661, BIT-mysql-client-2021-46661, CVE-2021-46661
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-46661
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.3

## Details
MariaDB through 10.5.9 allows an application crash in find_field_in_tables and find_order_in_list via an unused common table expression (CTE).

## References
- https://jira.mariadb.org/browse/MDEV-25766
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DKJRBYJAQCOPHSED43A3HUPNKQLDTFGD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZFZVMJL5UDTOZMARLXQIMG3BTG6UNYW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NJ4KDAGF3H4D4BDTHRAM6ZEAJJWWMRUO/
- https://mariadb.com/kb/en/security/
- https://security.netapp.com/advisory/ntap-20220221-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2021-46661
