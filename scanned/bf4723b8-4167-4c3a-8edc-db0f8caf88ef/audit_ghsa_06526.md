# [M] SurrealDB: `RELATE` overwrites existing edge records without `UPDATE` permission

## Summary
Severity: Medium
Advisory: GHSA-f82j-v89j-mf86
CWE: CWE-285
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-f82j-v89j-mf86
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
`RELATE` creates an edge record between two existing records, and SurrealDB enforces the `CREATE` permission on the edge table for this operation. When the statement included a `SET id = edge:existing` clause, however, the new edge's id ended up pointing at an record that was already in storage. Rather than failing because the target already existed — which is what a create operation should do — the storage layer silently overwrote the existing edge. A caller with `CREATE` permission could therefore replace any existing edge on the table, even without `UPDATE` permission for that record.

### Impact

An authenticated user with `CREATE` permission on an edge table could overwrite any existing record on that table — including edges they had no `UPDATE` permission for — by issuing a `RELATE` whose `SET id = …` resolved to the target record's id. The attack is integrity-only.

### Patches

A patch has been introduced that adds an explicit `Statement::Relate` arm using `put_record` instead of `set_record` when the create path is selected. Conflicting writes now return a `RecordExists` error.

- Versions 3.1.0 and later are not affected by this issue.

This is a behaviour change for applications that relied on RELATE … SET id = … to silently replace existing edges; after the patch those calls return RecordExists instead. Applications that need "create or replace" semantics should use UPSERT (which is correctly permission-gated for the update half).

### Workarounds

The defect only fires when the `RELATE` statement includes a `SET id = …` clause that resolves to an existing edge id. Applications that let SurrealDB auto-generate the edge id (the default — `RELATE a:1 -> edge -> b:1 SET <data>` with no `id` override) are not affected, because auto-generated ids do not collide with existing records.

Where applications must use `SET id = …` (for example, to produce deterministic edge ids for idempotency), they should first verify that no record with the target id exists before issuing the statement, or restrict `CREATE` permission on the edge table to principals trusted with `UPDATE` on the same table.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-f82j-v89j-mf86
- https://github.com/surrealdb/surrealdb/commit/79aef90d9baf56147d21f6dcea7a59189ade0eb3
- https://github.com/orgs/surrealdb/discussions/110
- https://github.com/surrealdb/surrealdb
