# [M] SurrealDB: Graph traversal bypasses table SELECT permissions

## Summary
Severity: Medium
Advisory: GHSA-vjjx-rfw4-rmfc
CWE: CWE-200, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-vjjx-rfw4-rmfc
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
An authenticated record or scope user could read records on any table reachable through a graph edge or `REFERENCES TO` back-reference, regardless of that table's `PERMISSIONS FOR select` clause.

Traversing `SELECT * FROM source->edge->target` returned full documents from `target` even when `target` was defined as `PERMISSIONS FOR select NONE`. The same bypass extended through multi-hop chains, so any table reachable by a sequence of edges from a readable starting point was exposed.

The root cause: `GraphEdgeScan` and `ReferenceScan` fetched records straight from storage without routing them through `Document::pluck_select`, so the target table's permission expression was never consulted.

### Impact

An authenticated record or scope user can read records on any table reachable through a chain of graph edges or back-references from a table they have `select` on, regardless of the target's `PERMISSIONS FOR select` clause. Confidentiality-only and bounded to the caller's current database — namespace and database isolation are unaffected.

### Patches

A new per-batch permission cache (`exec::permission::CachedTableSelect`) resolves each target table's `SELECT` permission once and filters yielded values through `check_permission_for_value`, matching the regular `SELECT` code path.

- Versions 3.1.0 and later are not affected.

### Workarounds

- Remove `select` permission on edge tables whose targets should be hidden.
- Use namespace or database isolation as the primary boundary where feasible.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-vjjx-rfw4-rmfc
- https://github.com/surrealdb/surrealdb
