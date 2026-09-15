# [C] MariaDB server has unsafe parameter handling in `wsrep_notify_cmd`

## Summary
Severity: Critical
Advisory: BIT-mariadb-2026-49261
Aliases: BIT-mariadb-min-2026-49261, BIT-mysql-client-2026-49261, CVE-2026-49261, GHSA-3p3m-4x7c-p4pw
Ecosystem: Bitnami
Published: 2026-06-13
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-49261
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=12.3.1 <12.3.2

## Details
MariaDB server is a community developed fork of MySQL server. Versions 10.6.1 through 10.6.26, 10.11.1 through 10.11.17, 11.4.1 through 11.4.11, 11.8.1 through 11.8.7, and 12.3.1 with  `wsrep_notify_cmd` enabled would execute shell commands embedded in the name of the joiner node. This is fixed in 10.6.27, 10.11.18, 11.4.12, 11.8.8, and 12.3.2. As a workaround, anyone who cannot upgrade now should disable `wsrep_notify_cmd`.

## References
- https://github.com/MariaDB/server/security/advisories/GHSA-3p3m-4x7c-p4pw
- https://jira.mariadb.org/browse/MDEV-39721
- https://nvd.nist.gov/vuln/detail/CVE-2026-49261
- https://access.redhat.com/errata/RHSA-2026:25143
- https://access.redhat.com/errata/RHSA-2026:25145
- https://access.redhat.com/errata/RHSA-2026:33093
- https://access.redhat.com/errata/RHSA-2026:33412
- https://access.redhat.com/errata/RHSA-2026:33464
- https://access.redhat.com/errata/RHSA-2026:33481
- https://access.redhat.com/errata/RHSA-2026:33482
- https://access.redhat.com/security/cve/CVE-2026-49261
- https://bugzilla.redhat.com/show_bug.cgi?id=2487957
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-49261.json
- https://access.redhat.com/errata/RHSA-2026:49522
- https://access.redhat.com/errata/RHSA-2026:52848
- https://access.redhat.com/errata/RHSA-2026:54142
