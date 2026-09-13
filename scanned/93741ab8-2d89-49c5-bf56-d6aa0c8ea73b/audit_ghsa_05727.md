# [M] Sliver Vulnerable to Pre-Auth Memory Exhaustion via NoEncoder Bypass

## Summary
Severity: Medium
Advisory: GHSA-hjr9-wj7v-7hv8
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-hjr9-wj7v-7hv8
Type: github-advisory

## Affected
- Go: `github.com/bishopfox/sliver` — affected >=1.5.0

## Details
### Summary
A specially crafted nonce routes unauthenticated requests through the NoEncoder path, where `startSessionHandler()` reads the entire request body without limits, allowing attacker-driven memory exhaustion and process crash.

### Details
- `server/encoders/encoders.go`: `EncoderFromNonce()` returns NoEncoder when `nonce % 65537 == 0` (lines 254-264); NoEncoder is a passthrough (`util/encoders/nop.go:22-32`).
- `server/c2/http.go`: `anonymousHandler()` routes requests with any encoder (including NoEncoder) to `startSessionHandler()` (lines 551-562).
- `server/c2/http.go`: `startSessionHandler()` uses `io.ReadAll(req.Body)` without a size cap (lines 564-643), unlike the authenticated path that uses `io.LimitedReader` (`readReqBody()`, lines 708-732).

### PoC
An attacker could send an HTTP POST with a nonce that is a multiple of 65537 (e.g., ?q=65537) so it is handled by startSessionHandler() with a NoEncoder, and advertise a very large Content-Length while streaming data. Because this handler uses io.ReadAll(req.Body) without a size limit, the server is expected to allocate large amounts of memory and may exhaust available RAM, leading to process termination on typical deployments.

### Impact
Unauthenticated remote DoS: attacker can crash the Sliver HTTP listener, dropping all active sessions and locking out operators until restart. No credentials or non-default config required.

## References
- https://github.com/BishopFox/sliver/security/advisories/GHSA-hjr9-wj7v-7hv8
- https://github.com/BishopFox/sliver
