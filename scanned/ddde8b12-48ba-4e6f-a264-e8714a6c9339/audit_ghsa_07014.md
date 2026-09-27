# [H] SurrealDB: HTTP RPC Session Race Condition Allows Privilege Escalation

## Summary
Severity: High
Advisory: GHSA-4vgr-h27g-cf9p
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-4vgr-h27g-cf9p
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
The HTTP `/rpc` endpoint has a time-of-check/time-of-use (TOCTOU) race condition on internal session state. When authenticated and unauthenticated requests are processed concurrently, the unauthenticated request can inherit the authenticated user's session and privileges. The `/rpc` endpoint is the primary interface used by all official SurrealDB SDKs.

The HTTP `/rpc` handler does not bind each incoming request to an isolated session context. Instead, concurrent requests share mutable authentication state. When an authenticated request sets the session context and an unauthenticated request races in before it is cleared, the unauthenticated request executes with the authenticated user's privileges.

The impact depends on the privilege level of the session that is hijacked. If a root or namespace-level user session is inherited, the attacker can read and modify any data, delete records, and create persistent namespace-level users. If a scoped record user session is inherited, the attacker is limited to that user's permissions.

The attack requires no credentials, tokens, or session knowledge — only the ability to send concurrent HTTP requests to the `/rpc` endpoint while legitimate authenticated traffic is active.

## Impact

An unauthenticated attacker who can reach the `/rpc` endpoint can escalate privileges by racing against any active authenticated session. The severity of the impact depends on the permissions of the user whose session was hijacked. This could include escalation to root user of SurrealDB instance

## Patches

Versions prior to SurrealDB `v3.1.0` are vulnerable.

A patch has been introduced that replaces the shared default session with per-request session isolation. Every `POST /rpc` request now allocates a fresh, server-side UUID and runs entirely within that session's scope for the duration of the request. The session-map signatures across the RPC protocol have been changed from `Option<Uuid>` to `Uuid` so the "default session" can no longer be represented at the type level, preventing future regressions of the same shape.

## Workarounds

There is no configuration-level mitigation that fully addresses this vulnerability. Network-level controls restricting access to the `/rpc` endpoint to trusted clients can reduce exposure.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-4vgr-h27g-cf9p
- https://github.com/surrealdb/surrealdb/commit/2f53e6e86d1b87e38300e714cfd7aede1abe4c3d
- https://github.com/surrealdb/surrealdb/commit/fd800fc7c55afcdc97057d18cf7cb7f83557e702
- https://github.com/surrealdb/surrealdb
