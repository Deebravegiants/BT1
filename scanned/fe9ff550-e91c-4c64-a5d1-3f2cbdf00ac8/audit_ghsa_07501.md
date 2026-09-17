# [M] SurrealDB: Scraping a TABLE with no available PERMISSIONS to current auth level

## Summary
Severity: Medium
Advisory: GHSA-98fx-66cf-fc7c
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-98fx-66cf-fc7c
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
A vulnerability was discovered where the user-supplied `WHERE` clause in a `SELECT` statement is evaluated against the full record data before `PERMISSIONS FOR SELECT WHERE` determines whether the principal is authorised to access that record. A side-effecting expression in the `WHERE` clause can exfiltrate record contents before the permission check runs. The same ordering bug affects the `SET`, `MERGE`, `CONTENT` and `PATCH` clauses of update-variant statements (`UPDATE`, `UPSERT-update`, `INSERT ON DUPLICATE KEY UPDATE`, `RELATE-update`).

This vulnerability is confined to the attacker's current database. It does not cross namespace or database isolation boundaries.

### Impact

An authenticated user — including Record and Scope users — can read the full contents of any table in the database they are authenticated against, bypassing `PERMISSIONS FOR SELECT WHERE` restrictions on those tables.

The most direct exfiltration method requires scripting functions to be enabled (`--allow-scripting` / `-A`). However, exfiltration via SurrealQL's `THROW` statement is also feasible without scripting functions, and timing-based side-channel extraction is possible in all configurations.

All tables within the attacker's current database, regardless of table-level `PERMISSIONS FOR SELECT WHERE` restrictions on those tables, are vulnerable to this attack. Tables in other databases within the same namespace, or within other namespaces, are not vulnerable.

### Patches

A patch has been introduced that runs `check_permissions_table` before any user-supplied expression is evaluated against the record. A new `check_pre_update` helper centralises this ordering on every update-variant code path. Regression tests covering `WHERE`, `SET`, `MERGE`, `CONTENT`, `INSERT ON DUPLICATE KEY UPDATE`, and `RELATE` with `THROW` side-effects are included.

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update may want to:

- **Disable scripting functions** if not required — remove the `-A` / `--allow-scripting` flag. This blocks the most direct exfiltration method but does not fully mitigate the vulnerability, as `THROW`-based and timing-based exfiltration remain possible.
- **Limit query access** — restrict the ability of untrusted principals to run arbitrary `SELECT` queries with user-controlled `WHERE` clauses.
- **Use namespace/database isolation** instead of table-level permissions as the primary security boundary where feasible, since the vulnerability is in table-level permission enforcement, not namespace or database isolation.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-98fx-66cf-fc7c
- https://github.com/surrealdb/surrealdb/commit/500f4060349580b9cbb9c07b8112a487551c4616
- https://github.com/surrealdb/surrealdb
