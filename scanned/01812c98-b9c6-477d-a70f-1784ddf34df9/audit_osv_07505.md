# [M] BIT-sqlite-2025-29088

## Summary
Severity: Medium
Advisory: BIT-sqlite-2025-29088
Aliases: CVE-2025-29088
Ecosystem: Bitnami
Published: 2025-04-16
Source: https://osv.dev/vulnerability/BIT-sqlite-2025-29088
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.49.0

## Details
In SQLite 3.49.0 before 3.49.1, certain argument values to sqlite3_db_config (in the C-language API) can cause a denial of service (application crash). An sz*nBig multiplication is not cast to a 64-bit integer, and consequently some memory allocations may be incorrect.

## References
- https://gist.github.com/ylwango613/d3883fb9f6ba8a78086356779ce88248
- https://github.com/sqlite/sqlite/commit/56d2fd008b108109f489339f5fd55212bb50afd4
- https://nvd.nist.gov/vuln/detail/CVE-2025-29088
- https://sqlite.org/forum/forumpost/48f365daec
- https://sqlite.org/releaselog/3_49_1.html
- https://www.sqlite.org/cves.html
