# [H] MariaDB: FILE privilege was not checked for subqueries in the FROM clause

## Summary
Severity: High
Advisory: BIT-mariadb-2026-44173
Aliases: BIT-mariadb-min-2026-44173, BIT-mysql-client-2026-44173, CVE-2026-44173, GHSA-667j-m53j-wpmc
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-44173
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=12.3.1 <12.3.2

## Details
MariaDB server is a community developed fork of MySQL server. From versions 10.6.1 to before 10.6.26, 10.11.1 to before 10.11.17, 11.4.1 to before 11.4.11, 11.8.1 to before 11.8.7, and 12.3.1, MariaDB allowed SELECT ... INTO OUTFILE and SELECT ... INTO DUMPFILE without verifying the FILE privilege if the FROM clause contained only subqueries. This issue has been patched in versions 10.6.26, 10.11.17, 11.4.11, 11.8.7, and 12.3.2.

## References
- https://github.com/MariaDB/server/security/advisories/GHSA-667j-m53j-wpmc
- https://jira.mariadb.org/browse/MDEV-39493
- https://nvd.nist.gov/vuln/detail/CVE-2026-44173
- https://access.redhat.com/errata/RHSA-2026:25143
- https://access.redhat.com/errata/RHSA-2026:25145
- https://access.redhat.com/errata/RHSA-2026:33093
- https://access.redhat.com/errata/RHSA-2026:33412
- https://access.redhat.com/errata/RHSA-2026:33464
- https://access.redhat.com/errata/RHSA-2026:33481
- https://access.redhat.com/errata/RHSA-2026:33482
- https://access.redhat.com/security/cve/CVE-2026-44173
- https://bugzilla.redhat.com/show_bug.cgi?id=2488460
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44173.json
- https://access.redhat.com/errata/RHSA-2026:49522
