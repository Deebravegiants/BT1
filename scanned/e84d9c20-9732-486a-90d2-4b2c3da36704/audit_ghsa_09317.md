# [H] Signal K Server's WebSocket Login Endpoint Lacks Rate Limiting (Credential Brute-Force)

## Summary
Severity: High
Advisory: GHSA-vmfm-ch9h-5c7g
CVE: CVE-2026-41893
CWE: CWE-307
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-vmfm-ch9h-5c7g
Type: github-advisory

## Affected
- npm: `signalk-server` — affected >=0 <2.25.0

## Details
## Summary

The HTTP login endpoints (`POST /login` and `POST /signalk/v1/auth/login`) are protected by `express-rate-limit` (default: 100 attempts per 10-minute window, configurable via `HTTP_RATE_LIMITS`). The WebSocket login path — sending `{login: {username, password}}` messages over an established WebSocket connection — calls `app.securityStrategy.login()` directly without any rate limiting.

An attacker can bypass HTTP rate limiting entirely by opening a WebSocket connection and attempting unlimited password guesses at the speed bcrypt allows (~20 attempts/sec with 10 salt rounds).

## Details

**Vulnerable code:** `src/interfaces/ws.ts`, function `processLoginRequest` (lines 753-780)

The function directly calls `app.securityStrategy.login(msg.login.username, msg.login.password)` with no throttling or attempt tracking.

**Rate-limited HTTP path for comparison:** `src/tokensecurity.ts` lines 609-617 apply `loginLimiter` middleware to the HTTP login routes at line 637.

## Steps to Reproduce

1. Start Signal K server with security enabled
2. Open a WebSocket connection to `ws://server:3000/signalk/v1/stream?subscribe=none`
3. Wait for the hello message
4. Send login attempts in rapid succession:
   ```json
   {"requestId": "1", "login": {"username": "admin", "password": "guess1"}}
   {"requestId": "2", "login": {"username": "admin", "password": "guess2"}}
   ```
5. Observe that all attempts are processed without any 429 response or throttling
6. For comparison, send 100+ HTTP POST requests to `/signalk/v1/auth/login` — the 101st returns 429

A POC script is available that demonstrates both the HTTP rate limiting working correctly and the WebSocket path accepting unlimited attempts.

## Impact

- Credential brute-forcing via the WebSocket protocol at ~20 attempts/sec (bcrypt-limited)
- Complete bypass of the HTTP rate limiting defense
- A single WebSocket connection is sufficient for unlimited attempts
- With multiple parallel connections, throughput multiplies
- A 10,000-word dictionary attack completes in ~8 minutes over a single connection

Signal K servers are commonly deployed on boat networks where they may be accessible to other devices on the same LAN.

## CWE

CWE-307: Improper Restriction of Excessive Authentication Attempts

## Suggested Fix

Track failed login attempts per remote IP in a shared store (or reuse the existing express-rate-limit store) that is checked in both the HTTP login middleware and the processLoginRequest WebSocket handler.

## Context

Found while building an open source maritime security scanner. Verified on v2.24.0 (current master).

Discovered by Mark Curphey

## References
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-vmfm-ch9h-5c7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-41893
- https://github.com/SignalK/signalk-server/pull/2568
- https://github.com/SignalK/signalk-server/commit/215d81eb700d5419c3396a0fbf23f2e246dfac2d
- https://github.com/SignalK/signalk-server
- https://github.com/SignalK/signalk-server/releases/tag/v2.25.0
