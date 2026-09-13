# [M] OpenClaw has auth inconsistency on local Browser Extension Relay /extension endpoint

## Summary
Severity: Medium
Advisory: GHSA-pfv7-rr5m-qmv6
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-pfv7-rr5m-qmv6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
### Summary

When the optional Chrome extension relay is enabled, `/extension` accepted unauthenticated WebSocket upgrades while `/json/*` and `/cdp` required auth.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.17`
- Latest published npm version at triage time: `2026.2.17`

### Impact

This is a local-only issue on loopback (`127.0.0.1`) and only applies when the extension relay feature is in use. A local process on the same machine could connect to `/extension` without the token and interfere with extension-relay behavior.

No remote network exploit path is involved.

### Fix

- Require gateway-token auth on both `/extension` and `/cdp` relay WebSocket endpoints.
- Keep loopback/origin checks as defense-in-depth, not as authentication.
- Use one token path in setup: `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN`.

### Fix Commit(s)

- `7e54b6c96feb1a5c30884f2b32037b8dadd0e532`

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-pfv7-rr5m-qmv6
- https://github.com/openclaw/openclaw/commit/7e54b6c96feb1a5c30884f2b32037b8dadd0e532
- https://github.com/openclaw/openclaw
