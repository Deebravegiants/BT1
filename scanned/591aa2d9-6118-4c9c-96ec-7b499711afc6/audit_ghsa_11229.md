# [H] @grackle-ai/server has Missing WebSocket Origin Header Validation

## Summary
Severity: High
Advisory: GHSA-w3hv-x4fp-6h6j
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-w3hv-x4fp-6h6j
Type: github-advisory

## Affected
- npm: `@grackle-ai/server` — affected >=0 <0.70.3

## Details
### Impact

The WebSocket upgrade handler in the server validates authentication (API key token or session cookie) but does not check the `Origin` header. A malicious webpage on a different origin could initiate a WebSocket connection to `ws://localhost:3000/ws` if it can leverage the user's session cookie (which is `SameSite=Lax`, allowing top-level navigations).

This enables **cross-origin WebSocket hijacking** — if a user visits a malicious site while a Grackle session is active, the attacker's page could open a WebSocket and subscribe to real-time events (session output, task updates, environment state).

**Affected code:**
- `packages/server/src/ws-bridge.ts:80-91` — connection handler accepts WebSocket upgrades without checking `req.headers.origin`

### Patches

**Fix:** Validate `req.headers.origin` against an allowlist before accepting connections:
```typescript
const origin = req.headers.origin || "";
if (origin && !origin.includes("localhost") && !origin.includes("127.0.0.1")) {
  ws.close(4003, "Invalid origin");
  return;
}
```

### Workarounds

Ensure the Grackle server is only accessible on `127.0.0.1` (the default). Do not use `--allow-network` in untrusted network environments.

### Resources

- CWE-346: Origin Validation Error
- File: `packages/server/src/ws-bridge.ts`

## References
- https://github.com/nick-pape/grackle/security/advisories/GHSA-w3hv-x4fp-6h6j
- https://github.com/nick-pape/grackle
