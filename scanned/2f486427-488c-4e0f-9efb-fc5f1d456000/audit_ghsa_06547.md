# [M] Node.js Adapter for Hono: Unauthenticated memory-leak DoS via aborted WebSocket handshake

## Summary
Severity: Medium
Advisory: GHSA-9mqv-5hh9-4cgg
CVE: CVE-2026-73565
CWE: CWE-401, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-9mqv-5hh9-4cgg
Type: github-advisory

## Affected
- npm: `@hono/node-server` — affected >=2.0.0 <2.0.10

## Details
## Summary

A WebSocket upgrade request to an `upgradeWebSocket` route with a missing or malformed `Sec-WebSocket-Key` header leaks memory permanently. The request's `IncomingMessage` is retained in an internal map and a pending promise is never settled, even though no connection is established. Since the route is reachable pre-handshake without authentication, an unauthenticated attacker can flood it to gradually exhaust memory.

## Details

The built-in WebSocket helper cleans up its internal map only on a successful handshake or when the route guard rejects the request. When `ws` aborts the handshake because `Sec-WebSocket-Key` is missing or malformed, no `connection` event is emitted, so neither cleanup path runs and the entry is retained forever. A present-but-malformed key leaks identically, so a proxy that only checks for the header's presence does not mitigate it.

## Impact

An unauthenticated attacker can flood any public `upgradeWebSocket` route with malformed-key upgrade requests, causing unbounded memory growth and eventual loss of availability. No confidentiality or integrity impact.

Reported by @TarPeg007.

## References
- https://github.com/honojs/node-server/security/advisories/GHSA-9mqv-5hh9-4cgg
- https://github.com/honojs/node-server/commit/3a21938c418340e980cb7ffa88e78369f78392d1
- https://github.com/honojs/node-server
- https://github.com/honojs/node-server/releases/tag/v2.0.10
