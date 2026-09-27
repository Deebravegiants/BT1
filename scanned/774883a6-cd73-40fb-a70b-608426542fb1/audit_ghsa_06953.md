# [H] QTINeon has unauthenticated relay-to-host amplification via unbounded RECONNECT_REQUEST forwarding

## Summary
Severity: High
Advisory: GHSA-85rg-p3fr-xc2f
CVE: CVE-2026-54609
CWE: CWE-400, CWE-406, CWE-770
Ecosystem: Maven, PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-85rg-p3fr-xc2f
Type: github-advisory

## Affected
- Maven: `com.quietterminal:qti-neon` — affected 1.0.0
- PyPI: `qti-neon` — affected 1.0.0
- npm: `qti-neon` — affected 1.0.0

## Details
### Impact
The relay's reconnect handler forwards every `RECONNECT_REQUEST` to the host without deduplication or a size cap on the `pendingReconnects` map, unlike the connect flow which guards against this with `maxPendingConnections`. An unauthenticated attacker who knows a valid session ID can send `RECONNECT_REQUEST` packets from many spoofed source addresses; each packet that passes the session lookup is forwarded to the host as a new reconnect attempt. Because the per-source rate limiter assigns a fresh token bucket to each spoofed IP, it provides no protection. The host receives one forwarded packet per spoofed source per cleanup cycle, making the relay an amplification vector for denial-of-service against the host. The host's real address is never exposed to clients by design, so this is the primary viable DoS path against it. A secondary issue: once more than `maxRateLimiters` spoofed IPs are seen, `performCleanup` calls `rateLimiters.clear()`, resetting rate limit state for all sources including legitimate ones.

Affected: `NeonRelay` in all three implementations (Java, Python, TypeScript).

### Patches
Not yet patched. Fix consists of three changes to handleReconnectRequest in each implementation:

1. Reject the request if `pendingReconnects.size() >= maxPendingConnections` (mirrors the existing connect-flow guard)
2. Only forward to the host if the `sessionId:clientId` key is not already present in `pendingReconnects` — the map entry can still be updated with the new source address, but the host only needs to validate once per slot
3. In `performCleanup`, evict throttled entries before falling back to `rateLimiters.clear()` to avoid resetting legitimate sources' rate limit state

### Workarounds
Operators can partially mitigate by placing the relay behind a network-level filter that drops packets with spoofed source addresses (BCP38/uRPF). This does not address the missing `pendingReconnects` size cap or the `rateLimiters.clear()` issue but eliminates the amplification path in most deployment environments.

### References
- PROTOCOL.md — reconnect flow
- ARCHITECTURE.md — reconnect handshake detail (step 4 describes the unbounded `put`)

## References
- https://github.com/Quiet-Terminal-Interactive/QTINeon/security/advisories/GHSA-85rg-p3fr-xc2f
- https://github.com/Quiet-Terminal-Interactive/QTINeon
