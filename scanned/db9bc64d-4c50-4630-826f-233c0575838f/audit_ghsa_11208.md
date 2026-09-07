# [M] @grackle-ai/powerline Runs Without Authentication by Default

## Summary
Severity: Medium
Advisory: GHSA-xq7h-vwjp-5vrh
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-xq7h-vwjp-5vrh
Type: github-advisory

## Affected
- npm: `@grackle-ai/powerline` — affected >=0 <0.70.1

## Details
### Impact

When `--token` is not provided and `GRACKLE_POWERLINE_TOKEN` is not set, the PowerLine gRPC server runs with **zero authentication**. A warning is logged (`"NO AUTH (development only)"`) but nothing prevents deployment in this state. Any client that can reach the PowerLine port can spawn agent sessions, access credential tokens, and execute code.

The default binding is `127.0.0.1` (loopback only), which limits exposure to the local machine. However, if PowerLine is accidentally exposed on a network (e.g., in a container or via port forwarding), the impact is critical.

**Affected code:**
- `packages/powerline/src/index.ts:46` — token defaults to empty string
- `packages/powerline/src/index.ts:63-76` — auth interceptor is only added when token is truthy

### Patches

0.70.1

**Fix:** Require an explicit `--no-auth` flag to run without authentication, rather than defaulting to no auth when the token is empty. Throw an error if starting without a token and without `--no-auth`.

### Workarounds

Always provide `--token` or set `GRACKLE_POWERLINE_TOKEN` when starting PowerLine. The Grackle server does this automatically when managing PowerLine lifecycle.

### Resources

- CWE-306: Missing Authentication for Critical Function
- File: `packages/powerline/src/index.ts`

## References
- https://github.com/nick-pape/grackle/security/advisories/GHSA-xq7h-vwjp-5vrh
- https://github.com/nick-pape/grackle
