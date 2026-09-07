# [M] SurrealDB: Crafting malicious LIVE queries writes to the database, resulting in DoS, without permission to the table required

## Summary
Severity: Medium
Advisory: GHSA-4v76-cw68-4vc9
CWE: CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-4v76-cw68-4vc9
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
A `LIVE` query whose `WHERE` clause evaluates to an error caused the source data modifier (the user creating, updating, or deleting a record on the watched table) to fail instead. Calling any arbitrary SurrealQL function with a typed parameter and passing a value of the wrong type — for example `LIVE SELECT * FROM t WHERE string::trim(deny)` — triggered an evaluation error inside the LIVE notification path. That error then propagated through to the triggering write, rolling back the attempted change.

While such a `LIVE` query was registered, all `CREATE`, `UPDATE`, and `DELETE` operations on the watched table failed — including those issued by a root user — for as long as the registration remained active. Registering the `LIVE` required `select` permission on the table; no other permission on the table was needed.

### Impact

An authenticated user with `select` permission on a table can prevent all `CREATE`, `UPDATE`, and `DELETE` operations on that table — by any other user, up to and including root — for the lifetime of a single registered `LIVE` query. Service is restored when the `LIVE` query is killed or the session that registered it ends.

### Patches

A patch has been introduced that:

1. **Decouples LIVE query evaluation errors from the source transaction** — when `lq_check` returns an error during the LIVE notification path, the error is now reported to the LIVE subscriber as an `Action::Error` notification and the LIVE processing path returns `Ok(())`. The triggering write proceeds normally.
2. **Defers the error notification until after the permission check** — the `Action::Error` notification is only delivered after the LIVE subscription's `PERMISSIONS` clause has been evaluated, so unauthorised subscribers do not learn even that an error occurred (closing an information-disclosure side channel introduced by the first part of the fix).

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Users unable to upgrade should restrict the ability of untrusted users to register `LIVE` queries by removing the `select` permission on tables they want to keep writeable, or by gating LIVE registration at the application layer.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-4v76-cw68-4vc9
- https://github.com/surrealdb/surrealdb/commit/af835eb199ad2327a04c42101d11aff21fce7e47
- https://github.com/surrealdb/surrealdb/commit/b29e03f0714d1c4ec091fc6f27f1edbe243b8aec
- https://github.com/surrealdb/surrealdb
