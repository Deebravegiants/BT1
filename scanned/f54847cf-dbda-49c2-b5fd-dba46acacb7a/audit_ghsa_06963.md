# [H] OpenClaw: Trusted-proxy Control UI WebSocket accepted client-declared scopes before pairing

## Summary
Severity: High
Advisory: GHSA-qjpc-qf9m-xwmr
CWE: CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-qjpc-qf9m-xwmr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

In trusted-proxy Control UI mode, OpenClaw accepted a WebSocket client's declared operator scopes before those scopes were bound to a server-approved pairing or trusted-proxy authorization baseline.

This issue affects trusted-proxy Control UI deployments. It does not apply to shared-secret Control UI sessions, which are treated as trusted operator sessions by design.

### Affected configurations

This affects deployments using `gateway.auth.mode: "trusted-proxy"` for Control UI access where a restricted trusted-proxy user could open a Control UI WebSocket and present a fresh, unpaired device identity with elevated requested scopes.

### Impact

An unpaired or restricted trusted-proxy Control UI client could obtain cached `operator.admin` authority on its live WebSocket connection. That authority could then be used for admin-gated Gateway RPCs until the connection was closed or revalidated.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Upgrade to `openclaw@2026.5.18` or later. Before upgrading, restrict trusted-proxy Control UI access to users who should have the scopes they can request, and restart the gateway after changing trusted-proxy authorization policy.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qjpc-qf9m-xwmr
- https://github.com/openclaw/openclaw
