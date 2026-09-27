# [M] SurrealDB: LIVE query subscriptions survive session state changes, bypassing access controls

## Summary
Severity: Medium
Advisory: GHSA-4m82-p8cx-f94j
CWE: CWE-613
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-4m82-p8cx-f94j
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
A `LIVE SELECT` subscription records the user's auth state (`$auth`, `$token`, `$session`, `$access`) when it is registered, and the server uses that recorded state to evaluate the table- and row-level `PERMISSIONS` clauses for every subsequent notification. The recorded state is never refreshed. 

When something changes the user's effective auth state — the originating session is invalidated, the session's TTL expires, or the user signs in, signs up, or authenticates as a different identity on the same connection — the subscription keeps delivering notifications under the old, stale auth state, and the `PERMISSIONS` that should now apply to the connection are never consulted.

### Impact

A user whose session has been revoked, expired, signed out of, or re-authenticated on the same connection continues to receive real-time notifications evaluated against the prior principal. The attacker does not gain access to new resources — only continued access to resources the prior principal was already permitted to read — but that continued access persists past the point the principal change should have ended it, and persists indefinitely until the originating connection is closed.

This is confidentiality-only: the dispatcher does not enable writes evaluated under the stranded principal.

### Patches

- **`invalidate()` and TTL expiry** — `RpcProtocol::invalidate` now calls `cleanup_lqs(session_id)` after clearing the session, dropping every LIVE owned by the now-invalidated session. The notification dispatcher additionally reads the originating session's `exp` and skips delivery once it has passed, closing the TTL-expiry leg without requiring the `Session` object to remain in memory.
- **Principal change on `signin` / `signup` / `authenticate` / `refresh`** — each of these RPC methods now snapshots the session's auth principal (`Auth::id()` + `Auth::level()`) before mutating the session and, if the principal has changed after the operation, calls `cleanup_lqs(session_id)`. Token refresh against the same identity is therefore preserved; identity change tears stranded subscriptions down.

Versions  3.1.0 and later are not affected by this issue.

### Workarounds

For unpatched versions, clients should call `reset()` (which tears down all LIVE queries owned by the session) or `kill` each outstanding `live query ID` before signing out, signing in as a different identity, or signing up on an existing connection. There is no client-side workaround for the TTL-expiry leg; deployments concerned about it should restrict `DURATION FOR SESSION` on access methods that have permission to register LIVE queries.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-4m82-p8cx-f94j
- https://github.com/surrealdb/surrealdb/commit/6cc48412c975d51b47617708ec44abc11ca5a89a
- https://github.com/surrealdb/surrealdb/commit/cbec0a73dc9575994d2b9c1aec26af539dc99878
- https://github.com/surrealdb/surrealdb
