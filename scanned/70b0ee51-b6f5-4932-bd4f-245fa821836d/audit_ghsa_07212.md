# [M] SurrealDB vulnerable to Denial of Service due to nested types annotations

## Summary
Severity: Medium
Advisory: GHSA-q8qp-67f9-wr3f
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-q8qp-67f9-wr3f
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
The SurrealDB type/kind parser did not enforce the configured recursion depth limit when parsing nested type annotations. The expression parser already enforced the limit for analogous constructs; the kind parser omitted it. An authenticated attacker could send a query with deeply nested type annotations (e.g., `array<option<array<option<...>>>>`) and exhaust server memory, crashing the process.

This is an incomplete fix for [GHSA-6r8p-hpg7-825g](https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6r8p-hpg7-825g), which addressed the same class of bug in the expression parser but did not cover the kind/type annotation parser code path.

### Impact

An authenticated user with query execution privileges can crash a SurrealDB server with a single WebSocket message containing deeply nested type annotations.

### Patches

A patch has been introduced that wraps `parse_concrete_kind` and the `OPTION<...>` arm of `parse_inner_kind` with `enter_object_recursion!`, bounding the recursive cycle `parse_concrete_kind → parse_inner_kind → parse_inner_single_kind → parse_concrete_kind` at the configured `object_recursion_limit` (default 100). Regression tests cover both cast and `DEFINE FIELD` paths.

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Restrict the ability of untrusted users to execute arbitrary queries via the `--deny-arbitrary-query` capability flag for the affected user classes (guest, record, or system). Disabling untrusted access to the WebSocket `/rpc` endpoint also prevents exploitation; the HTTP `/sql` endpoint's 1 MiB body limit constrains nesting to a depth where OOM is not feasible.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-q8qp-67f9-wr3f
- https://github.com/surrealdb/surrealdb/commit/61d509b766afdf67cc26d8203fd7dc583c8d77aa
- https://github.com/surrealdb/surrealdb
