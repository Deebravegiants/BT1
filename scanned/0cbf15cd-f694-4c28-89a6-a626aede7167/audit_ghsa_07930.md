# [C] OpenClaw's gateway connect could skip device identity checks when auth.token was present but not yet validated

## Summary
Severity: Critical
Advisory: GHSA-rv39-79c4-7459
CVE: CVE-2026-28472
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-rv39-79c4-7459
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.2

## Details
### Summary

The gateway WebSocket `connect` handshake could allow skipping device identity checks when `auth.token` was present but not yet validated.

### Details

In `src/gateway/server/ws-connection/message-handler.ts`, the device-identity requirement could be bypassed based on the *presence* of a non-empty `connectParams.auth.token` rather than a *validated* shared-secret authentication result.

### Impact

In deployments where the gateway WebSocket is reachable and connections can be authorized via Tailscale without validating the shared secret, a client could connect without providing device identity/pairing. Depending on version and configuration, this could result in operator access.

### Deployment Guidance

Per OpenClaw security guidance, the gateway should only be reachable from a trusted network and by trusted users (for example, restrict Tailnet users/ACLs when using Tailscale Serve).

If the gateway WebSocket is only reachable by trusted users, there is typically no untrusted party with network access to exploit this issue.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.1`
- Fixed: `>= 2026.2.2`

### Fix

Device-identity skipping now requires *validated* shared-secret authentication (token/password). Tailscale-authenticated connections without validated shared secret require device identity.

### Fix Commit(s)

- fe81b1d7125a014b8280da461f34efbf5f761575

Thanks @simecek for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rv39-79c4-7459
- https://nvd.nist.gov/vuln/detail/CVE-2026-28472
- https://github.com/openclaw/openclaw/commit/fe81b1d7125a014b8280da461f34efbf5f761575
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.2
- https://www.vulncheck.com/advisories/openclaw-device-identity-check-bypass-in-gateway-websocket-connect-handshake
