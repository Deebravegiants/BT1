# [M] SurrealDB: Field-level SELECT permissions bypassed via graph and reference traversals

## Summary
Severity: Medium
Advisory: GHSA-hv6h-hc26-q48p
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-hv6h-hc26-q48p
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=3.1.0 <3.1.5

## Details
A record user could read field values hidden from them by field-level SELECT permissions by reaching the records through a graph-edge (`->`) or back-reference (`<~`) traversal instead of a direct `SELECT`.

When a table was readable at the table level but carried a field hidden by a field-level permission (`DEFINE FIELD secret ON knows PERMISSIONS FOR select NONE`), a direct `SELECT * FROM knows` hid `secret` — but reaching the same records through a traversal that yields full objects — `person:bob->(SELECT * FROM knows)`, `person:bob<~(SELECT * FROM comment)`, or a projected target vertex `->knows->(SELECT * FROM person)` — returned it intact.

The root cause: the shared `resolve_record_batch` helper used by `GraphEdgeScan` (`FullEdge`) and `ReferenceScan` (`FullRecord`) enforced only the table-level SELECT permission and pushed raw record data, never running the field-level filtering (`build_field_state` / `filter_fields_by_permission`) that ordinary table scans and `fetch_record` apply.

### Impact

A record user can read the values of fields hidden by field-level SELECT permissions, on tables they already hold table-level SELECT on, by materialising the records through a graph-edge, back-reference, or target-vertex traversal — recovering the values directly, for every record the traversal returns.

The disclosure is confined to the field-permission layer: it grants **no unauthorised cross-table, cross-record, or cross-namespace/database access**. The table's own SELECT permission — including any row-level `WHERE` predicate — is still enforced, so the caller only reaches records they were already entitled to read; only the per-field SELECT filtering within those records is skipped. Root and record-owner sessions are unaffected, and data cannot be modified (confidentiality only).

Table-level enforcement on these traversals landed in 3.1.0 (the fix for GHSA-vjjx-rfw4-rmfc); releases before 3.1.0 additionally exposed whole records on tables the caller could not read, and are covered by that advisory.

### Patches

`resolve_record_batch` (the shared helper that materialises full records for graph and reference traversals) now applies field-level SELECT permissions and read-time `COMPUTED` fields to each record, matching the regular table-scan and `fetch_record` paths.

Versions 3.1.5 and later are not affected.

### Workarounds

- Force the unaffected legacy executor with `--planner-strategy compute-only` (env `SURREAL_PLANNER_STRATEGY`).
- Do not rely on field-level SELECT permissions to hide values on tables reachable as a graph edge, reference target, or traversal vertex; restrict at the table level instead.
- Use namespace / database isolation as the primary boundary where feasible.

### References

- [SurrealQL Documentation — DEFINE FIELD](https://surrealdb.com/docs/surrealql/statements/define/field)
- [SurrealQL Documentation — DEFINE TABLE … PERMISSIONS](https://surrealdb.com/docs/surrealql/statements/define/table)
- [SurrealQL Documentation — Graph relationships](https://surrealdb.com/docs/surrealql/datamodel/relationships)
- `fix(exec): apply field-level SELECT permissions + computed fields when graph/reference traversals materialize full records`

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-hv6h-hc26-q48p
- https://github.com/surrealdb/surrealdb
