# [C] MariaDB: mysql_real_escape_string() incorrectly handled big5

## Summary
Severity: Critical
Advisory: BIT-mariadb-2026-44172
Aliases: BIT-mariadb-min-2026-44172, BIT-mysql-client-2026-44172, CVE-2026-44172, GHSA-pv9p-5w55-55jm, PYSEC-2026-217
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-44172
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=3.3.18 <10.4.34

## Details
MariaDB server is a community developed fork of MySQL server. In versions 3.3.18 and 3.4.8, an application that was taking non-validated user input, escaping it with mysql_real_escape_string() and sending it to the database using text protocol and big5 character set was vulnerable to SQL injections, even though mysql_real_escape_string() was supposed to prevent them. This issue has been patched in versions 3.3.19 and 3.4.9.

## References
- https://github.com/MariaDB/server/security/advisories/GHSA-pv9p-5w55-55jm
- https://jira.mariadb.org/browse/CONC-819
- https://nvd.nist.gov/vuln/detail/CVE-2026-44172
- https://access.redhat.com/errata/RHSA-2026:33093
- https://access.redhat.com/errata/RHSA-2026:33412
- https://access.redhat.com/errata/RHSA-2026:33464
- https://access.redhat.com/errata/RHSA-2026:33481
- https://access.redhat.com/errata/RHSA-2026:33482
- https://access.redhat.com/security/cve/CVE-2026-44172
- https://bugzilla.redhat.com/show_bug.cgi?id=2488459
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44172.json
- https://access.redhat.com/errata/RHSA-2026:30135
- https://access.redhat.com/errata/RHSA-2026:43505
- https://access.redhat.com/errata/RHSA-2026:47772
