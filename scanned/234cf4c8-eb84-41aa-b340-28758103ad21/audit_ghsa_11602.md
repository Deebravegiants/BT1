# [M] OpenClaw: Gateway WebSocket Denial of Service via unbounded pre-auth upgrades

## Summary
Severity: Medium
Advisory: GHSA-f44p-c7w9-7xr7
CVE: CVE-2026-41399
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-f44p-c7w9-7xr7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

The gateway accepted unbounded concurrent unauthenticated WebSocket upgrades before allocating them to an authenticated session budget.

## Impact

An unauthenticated network attacker could consume socket and worker capacity and disrupt WebSocket availability for legitimate clients.

## Affected Component

`src/gateway/server-http.ts, src/gateway/server/preauth-connection-budget.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `cb5f7e201f` (`gateway: cap concurrent pre-auth websocket upgrades`).

Discovered by：Topsec AlphaLab (wang dong)

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f44p-c7w9-7xr7
- https://github.com/openclaw/openclaw/commit/cb5f7e201f3f86ad70e199ef850e636b4cc457ba
- https://github.com/openclaw/openclaw
