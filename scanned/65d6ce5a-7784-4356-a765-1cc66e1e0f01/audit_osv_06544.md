# [M] MariaDB: Authorization bypass in role-based routine-level privilege check exposes stored routine definitions

## Summary
Severity: Medium
Advisory: BIT-mariadb-2026-44169
Aliases: BIT-mariadb-min-2026-44169, BIT-mysql-client-2026-44169, CVE-2026-44169, GHSA-22xq-vq3f-87x2
Ecosystem: Bitnami
Published: 2026-06-16
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-44169
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=12.3.1 <12.3.2

## Details
MariaDB server is a community developed fork of MySQL server. From versions 11.4.1 to before 11.4.11, 11.8.1 to before 11.8.7, and 12.3.1, a user getting EXECUTE access to a stored routine via a role, could see the routine definition even without SHOW CREATE ROUTINE privilege. This issue has been patched in versions 11.4.11, 11.8.7, and 12.3.2.

## References
- https://github.com/MariaDB/server/security/advisories/GHSA-22xq-vq3f-87x2
- https://jira.mariadb.org/browse/MDEV-39288
- https://nvd.nist.gov/vuln/detail/CVE-2026-44169
