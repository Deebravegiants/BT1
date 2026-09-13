# [H] blaze: Unbounded WebSocket message aggregation in http4s-blaze-server

## Summary
Severity: High
Advisory: GHSA-7ppr-r889-mcf2
CVE: CVE-2026-73493
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-7ppr-r889-mcf2
Type: github-advisory

## Affected
- Maven: `org.http4s:http4s-blaze-server_2.13` — affected >=0 <0.23.18
- Maven: `org.http4s:http4s-blaze-server_2.13` — affected >=1.0.0-M1 <1.0.0-M42
- Maven: `org.http4s:http4s-blaze-server_2.12` — affected >=0 <0.23.18
- Maven: `org.http4s:http4s-blaze-server_3` — affected >=1.0.0-M1 <1.0.0-M42

## Details
## Summary

`http4s-blaze-server` aggregates the fragments of an incoming WebSocket
message with no limit on total size or fragment count. A client that
completes a WebSocket handshake can send an unterminated fragmented
message and drive unbounded heap growth in the server JVM, resulting in
denial of service via `OutOfMemoryError`.

## Impact

Any http4s application serving WebSocket routes over
`BlazeServerBuilder` is affected; no non-default configuration is required,
and `maxWebSocketBufferSize` does not bound the aggregate (it bounds only
individual frames). A single connection sending continuation frames that
never set FIN forces the server to buffer every fragment until the heap is
exhausted, terminating the JVM with `OutOfMemoryError` on the blaze
selector thread. Small fragments amplify the cost through per-frame object
overhead, so a modest volume of wire bytes is sufficient. Where the
WebSocket endpoint is reachable without authentication the attacker is
unauthenticated and remote; where the handshake requires a principal, any
authenticated client can still trigger it.

## Workarounds

- No blaze-server configuration bounds the aggregate; `maxWebSocketBufferSize`
  is not a mitigation.
- Terminate/limit WebSocket traffic at a fronting layer that enforces
  message-size and fragment limits, or disable WebSocket routes.
- Longer term: blaze is EOL upstream; plan migration to a maintained
  backend (e.g. ember).

## References
- https://github.com/http4s/blaze/security/advisories/GHSA-7ppr-r889-mcf2
- https://github.com/http4s/blaze/commit/173e8ca820a0d12110bfe409c72e9b9c3d28d471
- https://github.com/http4s/blaze/commit/2ae13a74d55209b6573d5228d1aa94f0361a75d0
- https://github.com/http4s/blaze/commit/fadbe6d0f7f59045425688d313c8d4804973d12f
- https://github.com/http4s/blaze
- https://github.com/http4s/blaze/releases/tag/v0.23.18
- https://github.com/http4s/blaze/releases/tag/v1.0.0-M42
