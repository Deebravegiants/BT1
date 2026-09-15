# [M] Etherpad addressed weak token RNG, login timing, plugin path handling, API request handling

## Summary
Severity: Medium
Advisory: GHSA-92hr-gmr6-h8cp
CWE: CWE-208, CWE-209, CWE-22, CWE-235, CWE-330
Ecosystem: npm
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-92hr-gmr6-h8cp
Type: github-advisory

## Affected
- npm: `ep_etherpad-lite` — affected >=0 <3.3.0

## Details
Fix: PR #7906 (ether/etherpad). A set of medium/low hardening fixes:

- **Weak RNG for tokens (CWE-330):** author/session/readonly IDs were generated with `Math.random()` (client and server). Now use `crypto.getRandomValues`.
- **Login timing / no failure delay (CWE-208/CWE-307):** the OIDC interaction login used a non-constant-time password compare with no failure delay. Now uses `crypto.timingSafeEqual` plus a uniform failure delay; user lookup is own-property only.
- **Plugin dependency path handling (CWE-22):** plugin dependency names from package.json were used to build filesystem paths without validation (admin-gated install). Now validated against the npm name grammar.
- **API parameter pollution (CWE-235):** `/api/2` merged all request headers into the API field set. Now forwards only `authorization`, matching the openapi.ts handler.
- **Pad-creation side effect:** `API.appendChatMessage` could create arbitrary pads (missing `getPadSafe`). Now requires the pad to exist.
- **Error info disclosure (CWE-209):** the admin file server echoed filesystem error detail; now returns a generic message.

## References
- https://github.com/ether/etherpad/security/advisories/GHSA-92hr-gmr6-h8cp
- https://github.com/ether/etherpad/pull/7906
- https://github.com/ether/etherpad/commit/7ea99706483443239bbbc0f2df9aff8ab5de4805
- https://github.com/ether/etherpad
- https://github.com/ether/etherpad/releases/tag/3.3.0
