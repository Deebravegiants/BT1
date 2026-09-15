# [M] SurrealDB: Authenticated callers can read fields hidden by field-level SELECT permissions via error messages

## Summary
Severity: Medium
Advisory: GHSA-6g9v-7gq3-p2c6
CWE: CWE-209
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-6g9v-7gq3-p2c6
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
A record user with UPDATE access could read field values that field-level SELECT permissions hid from them. Arithmetic operators and `extend` embedded the raw operand into their error messages, and UPDATE permission checks evaluate against the unreduced document — so triggering such an error against a hidden field returned its value in the resulting error.

### Impact

A record user issues an UPDATE that performs an incompatible operation against a hidden field — e.g. `UPDATE person:me SET probe = email + 1` when `email` is a string — and reads the value from the returned error (`Tried to compute "alice@example.com" + 1 …`). One field per operation, but the attacker can repeat against any field on any record they can UPDATE.

### Patches

A patch has been introduced that replaces the raw operand in every `try_*` operator and in `extend` with the operand's type name (`"string"`, `"int"`, `"array"`, etc.).

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update should not grant UPDATE permission on records whose field-level SELECT permissions are expected to hide values from the same caller.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6g9v-7gq3-p2c6
- https://github.com/surrealdb/surrealdb/commit/0aaa332c79195e4c40275eb5224aed3d52f5cf90
- https://github.com/surrealdb/surrealdb
