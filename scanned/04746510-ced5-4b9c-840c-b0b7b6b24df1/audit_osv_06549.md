# [C] MariaDB: unsafe usage of `wsrep_sst_receive_address` values on the joiner side

## Summary
Severity: Critical
Advisory: BIT-mariadb-2026-48165
Aliases: BIT-mariadb-min-2026-48165, BIT-mysql-client-2026-48165, CVE-2026-48165, GHSA-7v3p-h23x-8hwv
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-48165
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=12.3.1 <12.3.2

## Details
MariaDB server is a community developed fork of MySQL server. From versions 10.6.1 to before 10.6.27, 10.11.1 to before 10.11.18, 11.4.1 to before 11.4.12, 11.8.1 to before 11.8.8, and 12.3.1, a high-privileged MariaDB user could've used wsrep_sst_receive_address or wsrep_sst_donor global system variables to execute shell commands as the uid of the mariadbd process on the galera joiner node. This issue has been patched in versions 10.6.27, 10.11.18, 11.4.12, 11.8.8, and 12.3.2.

## References
- https://github.com/MariaDB/server/security/advisories/GHSA-7v3p-h23x-8hwv
- https://jira.mariadb.org/browse/MDEV-39676
- https://nvd.nist.gov/vuln/detail/CVE-2026-48165
- https://access.redhat.com/errata/RHSA-2026:25143
- https://access.redhat.com/errata/RHSA-2026:25145
- https://access.redhat.com/errata/RHSA-2026:33093
- https://access.redhat.com/errata/RHSA-2026:33412
- https://access.redhat.com/errata/RHSA-2026:33464
- https://access.redhat.com/errata/RHSA-2026:33481
- https://access.redhat.com/errata/RHSA-2026:33482
- https://access.redhat.com/security/cve/CVE-2026-48165
- https://bugzilla.redhat.com/show_bug.cgi?id=2488458
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48165.json
- https://access.redhat.com/errata/RHSA-2026:49522
