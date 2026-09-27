# [H] SurrealDB has Denial of Service in JSON parser due to nested objects

## Summary
Severity: High
Advisory: GHSA-q729-696q-g9pq
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-q729-696q-g9pq
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
The SurrealDB value and JSON parser did not enforce the configured recursion depth limit when parsing nested `{`, `[`, or `(` tokens. The expression parser already enforced the limit for these tokens; the value/JSON parser omitted it. An unauthenticated attacker could send a deeply nested JSON payload to the WebSocket `/rpc` endpoint and exhaust server memory, crashing the process.

This is an incomplete fix for [GHSA-6r8p-hpg7-825g](https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6r8p-hpg7-825g), which addressed the same class of bug in the expression parser but did not cover the value/JSON parser code path.

### Impact

An unauthenticated remote attacker can crash a SurrealDB server with a single WebSocket message. No credentials or query execution privileges are required.

### Patches

A patch enforces the configured recursion depth limit in `parse_value` and `parse_json`, bringing them in line with the rest of the parser.

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Restrict network access to the WebSocket `/rpc` endpoint to trusted clients.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-q729-696q-g9pq
- https://github.com/surrealdb/surrealdb/commit/1bd9826f477f4089134460dc5574b6f4e6916973
- https://github.com/surrealdb/surrealdb
