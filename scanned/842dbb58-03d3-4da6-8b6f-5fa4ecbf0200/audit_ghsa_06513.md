# [M] SurrealDB: Edge PERMISSIONS FOR delete bypassed when a connected node is deleted

## Summary
Severity: Medium
Advisory: GHSA-whwg-vh4f-pmmf
CVE: CVE-2026-49997
CWE: CWE-285, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-whwg-vh4f-pmmf
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
In SurrealDB, records can be connected as a graph: a `RELATE` statement creates an edge record between two node records. If either endpoint node is deleted, SurrealDB automatically removes the edge row to keep the graph consistent.

A user with permission to delete a node could also delete the edges connected to that node, even when the edge table's `PERMISSIONS FOR delete` clause should have stopped them.

The automatic edge removal (`Document::purge_edges`) ran with permissions disabled (`opt.clone().with_perms(false)`), so the edge table's `PERMISSIONS FOR delete` and `PERMISSIONS FOR select` clauses were never consulted. The removal step could also observe edge state that the edge's SELECT clause should have hidden.

### Impact

What an attacker **can** do:

- Delete any edge connected to a node they can delete, regardless of the edge table's `PERMISSIONS FOR delete` clause.
- Observe edge contents that `PERMISSIONS FOR select` should have hidden, as a side effect of the same edge-removal step.

What it **can't** do:

- Delete nodes on tables they do not hold `DELETE` on (the edge removal only runs from an authorised node delete).
- Cross namespace or database isolation boundaries.
- Escalate to root or operator-level privileges.

### Patches

`Document::purge_edges` now propagates the caller's permission context into the edge removal. Each connected edge `DELETE` is evaluated against the edge table's `PERMISSIONS FOR delete` clause, matching a direct `DELETE`.

Versions 3.1.0 and later are not affected.

### Workarounds

- Restrict node `DELETE` permission to principals trusted to delete all connected edge records.
- Use namespace or database isolation as the primary boundary where edge-level `PERMISSIONS` is load-bearing for multi-tenant separation.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-whwg-vh4f-pmmf
- https://nvd.nist.gov/vuln/detail/CVE-2026-49997
- https://github.com/surrealdb/surrealdb/pull/242
- https://github.com/surrealdb/surrealdb/commit/500f4060349580b9cbb9c07b8112a487551c4616
- https://github.com/surrealdb/surrealdb/commit/a80d1784cf75358441978bbd77688855e95f4578
- https://github.com/surrealdb/surrealdb
- https://github.com/surrealdb/surrealdb/releases/tag/v3.1.0
