# [H] SurrealDB: HTTP /rpc `sessions` method leaks attached session UUIDs, enabling full session hijack by anonymous callers

## Summary
Severity: High
Advisory: GHSA-5qfp-32cf-69jh
CWE: CWE-384
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-5qfp-32cf-69jh
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
The HTTP `/rpc` `sessions` method returned every attached session UUID without authentication, and the `/rpc` handler accepted an arbitrary `session` field with no ownership check. An anonymous caller could enumerate UUIDs and impersonate any authenticated session.

"Attached" means sessions registered via `{"method":"attach"}` — the only writer to the HTTP session map. Ordinary stateless `/rpc` requests use ephemeral per-request sessions that are filtered from `sessions()` and destroyed at end-of-request, so they are not enumerable.

### Exposure

- **Exposed:** clients that issue `attach`, notably the official Rust SDK's `Http`/`Https` engine (auto-attaches once per `Surreal` handle).
- **Not exposed:** REST endpoints (`/sql`, `/key`, `/signin`, `/export`, etc.); WebSocket `/rpc` (per-connection scope, `attach` refused); embedded / MCP usage; ad-hoc `POST /rpc` callers that never `attach`.

### Impact

For each **attached and authenticated** session, an unauthenticated attacker can read, write, and delete any data the session can reach, dump metadata, invalidate sessions, and escalate to that session's privilege level (up to root). An attached session that has not yet authenticated is `Level::No` and confers no privilege.

### Patches

1. HTTP `sessions()` now returns `method_not_allowed`. WebSocket retains per-connection enumeration.
2. The HTTP `/rpc` handler gates client-supplied session IDs against the caller's request-level auth principal (actor id + level); mismatches return `session_not_found`.
3. Attached HTTP sessions are capped via `SURREAL_HTTP_MAX_ATTACHED_SESSIONS`.

Versions 3.1.0 and later are not affected.

### Workarounds

No configuration-level mitigation fully addresses this. For Users unable to upgrade:

- Avoid SDKs and client flows that call `attach` against HTTP `/rpc` (notably the Rust SDK's `Http`/`Https` engine). Prefer the WebSocket transport, or REST endpoints (`/sql`, `/signin`, `/key`, `/export`) which never populate the attached-session map.
- Restrict `/rpc` to trusted clients at the network layer.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-5qfp-32cf-69jh
- https://github.com/surrealdb/surrealdb/commit/fd800fc7c55afcdc97057d18cf7cb7f83557e702
- https://github.com/surrealdb/surrealdb
