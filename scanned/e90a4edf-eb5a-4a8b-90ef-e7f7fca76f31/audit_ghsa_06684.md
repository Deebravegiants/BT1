# [M] SurrealDB vulnerable to pre-auth memory amplification via unbounded `/sql` WebSocket frames

## Summary
Severity: Medium
Advisory: GHSA-65rj-r9fh-jp2v
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-65rj-r9fh-jp2v
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
An anonymous caller could degrade `/sql` availability by streaming WebSocket frames many times larger than the operator-configured per-connection limit. The `/sql` upgrade handler accepted anonymous connections and did not propagate `SURREAL_WEBSOCKET_MAX_MESSAGE_SIZE` to the WebSocket protocol layer — incoming bytes accumulated in the per-connection read buffer before `check_anon` could reject the query, so the memory cost was incurred regardless of whether the caller could ever execute SurrealQL. The same upgrade path also silently ignored `--deny-http sql` and `--deny-arbitrary-query *` for authenticated callers, but that secondary effect does not grant new permissions.

### Impact

`SURREAL_WEBSOCKET_MAX_MESSAGE_SIZE` is not applied to anonymous `/sql` connections, so each connection can buffer up to the WebSocket library defaults (16 MiB per frame, 64 MiB per reassembled message) of in-flight bytes regardless of the operator's configured limit. Holding this much memory pinned requires actively streaming bytes into the connection, so an attacker has to maintain bandwidth across many concurrent connections to consume meaningful memory. Within that constraint the result is degraded availability for legitimate `/sql` clients; on memory-constrained deployments the process may be OOM-killed and restarted during the attack rather than denied service outright.

Separately, `--deny-http sql` and `--deny-arbitrary-query *` were not enforced on the WebSocket, so SurrealQL operations the operator had configured to refuse could still be issued by any authenticated principal that already held the corresponding data permissions. This is a configuration-correctness defect — the bypass does not grant new permissions.

### Patches

A patch has been introduced that performs the two capability checks before calling `on_upgrade` and applies the same per-connection size limits used by `/rpc`. The capability checks enforce the operator's configured deny flags; they do not change what any authenticated principal is permitted to do.

- Versions 3.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update should refuse `GET /sql` requests carrying `Upgrade: websocket` at a reverse proxy, or apply per-connection frame size limits at the reverse proxy.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-65rj-r9fh-jp2v
- https://github.com/surrealdb/surrealdb/commit/899967e6a9cf064c88a4bc4b35ea7e2da28a6411
- https://github.com/surrealdb/surrealdb
