# [H] SurrealDB has unauthenticated remote DoS via malformed RPC `use` call

## Summary
Severity: High
Advisory: GHSA-wjjj-24cx-f28g
CWE: CWE-248, CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-wjjj-24cx-f28g
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
A single unauthenticated WebSocket message to `/rpc` crashed the SurrealDB server. Sending `use { db: "x" }` without first selecting a namespace hit `.expect("namespace should be set")` in the `use` handler; because `surrealdb-core` is built with `panic = 'abort'`, the panic terminated the process. `use` is callable before `signin`, and the per-method capability check passes by default for guest callers — so no credentials, token, or `--allow-guests` flag are required.

### Impact

An unauthenticated remote attacker who could reach the `/rpc` endpoint could crash the SurrealDB server with a single WebSocket message. No credentials, token, session knowledge, or capability are required.

### Patches

A patch has been introduced that returns a typed `invalid_params` response when `db` is set on a session with no `ns`, replacing the panic.

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update should restrict network access to the `/rpc` endpoint to trusted clients, and run SurrealDB under a process supervisor that restarts on crash.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-wjjj-24cx-f28g
- https://github.com/surrealdb/surrealdb/commit/1537ec4fbd789c61a5b43b648a854577dbe31a34
- https://github.com/surrealdb/surrealdb
