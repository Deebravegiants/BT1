# [H] MariaDB: path traversal in mbstream

## Summary
Severity: High
Advisory: BIT-mariadb-2026-44171
Aliases: BIT-mariadb-min-2026-44171, BIT-mysql-client-2026-44171, CVE-2026-44171, GHSA-9pjh-5hhw-65v9
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-44171
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=12.3.1 <12.3.2

## Details
MariaDB server is a community developed fork of MySQL server. From versions 10.6.1 to before 10.6.26, 10.11.1 to before 10.11.17, 11.4.1 to before 11.4.11, 11.8.1 to before 11.8.7, and 12.3.1, mbstream did not check for /../ in the path when unpacking the archive. A proper backup can never contain such paths, but a specially crafted archive could have caused mbstream to create files outside of the target-dir path. This issue has been patched in versions 10.6.26, 10.11.17, 11.4.11, 11.8.7, and 12.3.2.

## References
- https://github.com/MariaDB/server/security/advisories/GHSA-9pjh-5hhw-65v9
- https://jira.mariadb.org/browse/MDEV-39408
- https://nvd.nist.gov/vuln/detail/CVE-2026-44171
