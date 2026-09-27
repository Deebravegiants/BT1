# [H] BIT-mariadb-2021-27928

## Summary
Severity: High
Advisory: BIT-mariadb-2021-27928
Aliases: BIT-mariadb-min-2021-27928, BIT-mysql-client-2021-27928, CVE-2021-27928
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2021-27928
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0 <10.5.9

## Details
A remote code execution issue was discovered in MariaDB 10.2 before 10.2.37, 10.3 before 10.3.28, 10.4 before 10.4.18, and 10.5 before 10.5.9; Percona Server through 2021-03-03; and the wsrep patch through 2021-03-03 for MySQL. An untrusted search path leads to eval injection, in which a database SUPER user can execute OS commands after modifying wsrep_provider and wsrep_notify_cmd. NOTE: this does not affect an Oracle product.

## References
- http://packetstormsecurity.com/files/162177/MariaDB-10.2-Command-Execution.html
- https://jira.mariadb.org/browse/MDEV-25179
- https://lists.debian.org/debian-lts-announce/2021/03/msg00028.html
- https://mariadb.com/kb/en/mariadb-10237-release-notes/
- https://mariadb.com/kb/en/mariadb-10328-release-notes/
- https://mariadb.com/kb/en/mariadb-10418-release-notes/
- https://mariadb.com/kb/en/mariadb-1059-release-notes/
- https://mariadb.com/kb/en/security/
- https://security.gentoo.org/glsa/202105-28
- https://nvd.nist.gov/vuln/detail/CVE-2021-27928
