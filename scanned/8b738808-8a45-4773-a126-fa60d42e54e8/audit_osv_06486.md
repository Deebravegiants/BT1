# [M] BIT-mariadb-2021-46659

## Summary
Severity: Medium
Advisory: BIT-mariadb-2021-46659
Aliases: BIT-mariadb-min-2021-46659, BIT-mysql-client-2021-46659, CVE-2021-46659
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-46659
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.2

## Details
MariaDB before 10.7.2 allows an application crash because it does not recognize that SELECT_LEX::nest_level is local to each VIEW.

## References
- https://jira.mariadb.org/browse/MDEV-25631
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DKJRBYJAQCOPHSED43A3HUPNKQLDTFGD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EZFZVMJL5UDTOZMARLXQIMG3BTG6UNYW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NJ4KDAGF3H4D4BDTHRAM6ZEAJJWWMRUO/
- https://mariadb.com/kb/en/security/
- https://security.netapp.com/advisory/ntap-20220311-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2021-46659
