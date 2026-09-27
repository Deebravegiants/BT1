# [M] Gorilla WebSocket Uses Cryptographically Weak PRNG for WebSocket Mask Key

## Summary
Severity: Medium
Advisory: GHSA-w67g-5rqw-f597
CWE: CWE-338
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-w67g-5rqw-f597
Type: github-advisory

## Affected
- Go: `github.com/gorilla/websocket` — affected >=0 <1.5.3

## Details
gorilla/websocket used `math/rand` (cryptographically weak pseudo-random number generator) to generate WebSocket frame mask keys prior to commit d67f4185. WebSocket masking keys MUST be unpredictable to prevent frame content injection attacks. math/rand produces deterministic output when seeded with a known value, enabling an attacker to predict or recover mask keys and inject content into WebSocket connections.

**Type:** Use of Cryptographically Weak Pseudo-Random Number Generator
**Fix:** Replaced math/rand with crypto/rand (commit d67f4185, released in v1.5.3)
**Credit:** bounty-hunter v6.0 silent-fix detection

## References
- https://github.com/canolgun-commits/websocket/security/advisories/GHSA-w67g-5rqw-f597
- https://github.com/gorilla/websocket/commit/d67f41855da42d7bccd9ef050c49f7e54e783b95
- https://github.com/canolgun-commits/websocket
- https://github.com/gorilla/websocket/releases/tag/v1.5.3
