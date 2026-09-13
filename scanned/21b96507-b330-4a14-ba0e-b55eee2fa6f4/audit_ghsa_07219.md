# [M] SurrealDB has bypass of field-level SELECT permissions through JSON Patch `copy` and `move` with empty `from`

## Summary
Severity: Medium
Advisory: GHSA-fpxg-5xmv-922m
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-fpxg-5xmv-922m
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
SurrealDB lets callers modify records using JSON Patch operations via the `UPDATE … PATCH` statement (and SDK equivalents such as `db.patch()`). One of those operations is `copy`, which duplicates one field's value into another field of the same record. A `PATCH` with an empty `from` — for example, `UPDATE thing:1 PATCH [{ op: 'copy', from: '', path: '/leak' }]` — was treated as "copy the entire record" and duplicated every field, including fields the caller has no permission to read, into the destination field the caller chose. The permission filter that hides protected field values from the response only knew to hide the *original* protected field names, not the new destinations, so the protected values were returned to the caller intact under the new field name.

### Impact

An authenticated user with permission to issue `UPDATE … PATCH` against a record could read the values of any field on that record, regardless of field-level `PERMISSIONS FOR select` restrictions. The leak is confidentiality-only, and bounded to the fields of the single record the caller targets per PATCH request — it does not expose other records on the same table or any data outside that record's scope.

### Patches

A patch has been introduced that rejects an empty `from` pointer at parse time for both `copy` and `move` operations.

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update should restrict `UPDATE … PATCH` to callers who already hold SELECT permission on every field of the target record — for them, the bug exposes nothing they can't already read. Otherwise, switch the mutation to an explicit `SET` or `MERGE` clause, which removes the attack surface since neither form accepts JSON Patch operations.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-fpxg-5xmv-922m
- https://github.com/surrealdb/surrealdb/commit/56a7a1540d9228f82fd6284c258344e8dcb690fd
- https://github.com/surrealdb/surrealdb
