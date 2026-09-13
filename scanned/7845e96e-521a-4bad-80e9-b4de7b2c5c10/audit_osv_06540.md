# [C] Heap-based Buffer Overflow in MariaDB

## Summary
Severity: Critical
Advisory: BIT-mariadb-2026-32710
Aliases: BIT-mariadb-min-2026-32710, BIT-mysql-client-2026-32710, CVE-2026-32710, GHSA-4rj5-2227-9wgc
Ecosystem: Bitnami
Published: 2026-03-25
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-32710
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=12.1.2 <12.2.2

## Details
MariaDB server is a community developed fork of MySQL server. An authenticated user can crash MariaDB versions 11.4 before 11.4.10 and 11.8 before 11.8.6 via a bug in JSON_SCHEMA_VALID() function. Under certain conditions it might be possible to turn the crash into a remote code execution. These conditions require tight control over memory layout which is generally only attainable in a lab environment. This issue is fixed in MariaDB 11.4.10, MariaDB 11.8.6, and MariaDB 12.2.2.

## References
- https://github.com/MariaDB/server/security/advisories/GHSA-4rj5-2227-9wgc
- https://jira.mariadb.org/browse/MDEV-38356
- https://nvd.nist.gov/vuln/detail/CVE-2026-32710
