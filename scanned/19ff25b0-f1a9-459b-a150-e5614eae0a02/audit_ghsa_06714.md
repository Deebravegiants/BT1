# [M] SurrealDB: Authenticated subscribers can read records hidden by SELECT permissions via LIVE subscriptions

## Summary
Severity: Medium
Advisory: GHSA-6wqw-vhfr-9999
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-6wqw-vhfr-9999
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
A record user could read records the table's SELECT permission expression should have hidden, when that expression referenced `$value`, `$before`, `$after`, or `$event`. Binding a chosen value to that name before registering a `LIVE SELECT` caused notifications to evaluate the permission against the attacker's input instead of the real document.

### Impact

A record user binds a value to `$value`, `$before`, `$after`, or `$event` (e.g. `LET $value = [$auth.id]`) and registers `LIVE SELECT * FROM person`. The captured value shadows the real document at notification time, so a SELECT permission like `WHERE $auth.id.id() IN $value` passes for every record on the table — the subscriber receives notifications for records they should not see.

Read-only impact, bounded to one table. Permission expressions that reference only field names, `$auth`, or `$session` are unaffected.

### Patches

A patch has been introduced that re-orders the LIVE notification parameter binding so captured user variables are added first and the trusted document-context and session parameters are added last.

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update should avoid table-`PERMISSIONS` and LIVE `WHERE` expressions that read user-named variables (`$value`, `$before`, `$after`, `$event`) without also gating on a system-derived field such as the record id.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6wqw-vhfr-9999
- https://github.com/surrealdb/surrealdb/commit/6bcc55c9c0494a0d4d36821019b54459f7162af7
- https://github.com/orgs/surrealdb/discussions/101
- https://github.com/surrealdb/surrealdb
