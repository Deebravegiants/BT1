# [M] Better Auth: OAuth callback accepts mismatched `state` when cookie-backed state storage is used without PKCE

## Summary
Severity: Medium
Advisory: GHSA-wxw3-q3m9-c3jr
CWE: CWE-287, CWE-345, CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-wxw3-q3m9-c3jr
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.6.2

## Details
### Am I affected?

Users are affected if all of the following are true:

- The application uses `better-auth` at a version below `1.6.2` (or `@better-auth/sso` paired with such a version).
- `betterAuth({ account: { storeStateStrategy } })` is set to `"cookie"`. The default `"database"` is not affected.
- The application wires at least one OAuth provider through `genericOAuth({ config })` with `pkce: false`, or it supplies a custom `getToken` or `tokenUrl` that does not require the stored `codeVerifier`. Stock social providers with PKCE on are not affected.
- The provider returns arbitrary `code` values to the configured callback URL.

If users are on `better-auth@1.6.2` or later, they are not affected.

Fix:

1. Upgrade to `better-auth@1.6.2` or later (current stable is `1.6.10`).
2. If users cannot upgrade, see workarounds below.

### Summary

In `parseGenericState`, the cookie branch decrypted the `oauth_state` cookie and validated expiry, but did not compare the incoming OAuth `state` query parameter to the nonce that `generateGenericState` issued at sign-in. Any callback to `/api/auth/oauth2/callback/<providerId>` that arrived with a forged `state` and any `code` was therefore accepted as long as the browser still held a live `oauth_state` cookie. With `pkce: false` (or any `getToken` path that does not enforce a code-verifier round-trip), an attacker who forced the victim to deliver an attacker-controlled authorization code to the callback would mint a session bound to the attacker's external identity in the victim's browser. Account-linking flows behaved the same way, binding the attacker's external account to an authenticated victim row.

### Details

The cookie branch of `parseGenericState` did not compare the cookie's stored nonce to the incoming `state` parameter. The database branch (the default) was not affected because the verification row is keyed by `state` and the lookup itself enforces equality.

The fix re-binds the cookie to the nonce: `generateGenericState` writes `oauthState: state` into the encrypted payload before storage, and `parseGenericState` rejects when `parsedData.oauthState !== state`. The same primitive covers every caller (`generic-oauth`, social, account-link, oauth-proxy passthrough, OIDC SSO, SAML relay state).

### Patches

Fixed in `better-auth@1.6.2` via [PR #8949](https://github.com/better-auth/better-auth/pull/8949) (commit `9deb7936a`, merged 2026-04-09). The cookie branch of `parseGenericState` now rejects when the encrypted payload's nonce does not match the incoming `state` parameter; the database branch gained a defense-in-depth equality check.

### Workarounds

If users cannot upgrade immediately:

- **Switch `storeStateStrategy` back to `"database"`** (the default). This closes the cookie-only bypass without a code change.
- **Enable `pkce: true`** on every affected `genericOAuth` provider. The `codeVerifier` is the missing primitive that the attacker cannot supply.

### Impact

- **Forced-login (CSRF on OAuth callback)**: the attacker forces the victim's browser into an authenticated session bound to the attacker's external identity, allowing the attacker to observe the victim's actions inside the application.
- **Persistent account linking**: account-link flows bind the attacker's external account to the victim's authenticated row, granting persistent access until the link is removed.

### Credit

Reported by @Jvr2022 via private advisory disclosure, and by @alavesa (PatchPilots audit) via the public duplicate [issue #8897](https://github.com/better-auth/better-auth/issues/8897).

### Resources

- [CWE-352: Cross-Site Request Forgery (CSRF)](https://cwe.mitre.org/data/definitions/352.html)
- [CWE-345: Insufficient Verification of Data Authenticity](https://cwe.mitre.org/data/definitions/345.html)
- [CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)
- [RFC 6749 §10.12: Cross-Site Request Forgery](https://datatracker.ietf.org/doc/html/rfc6749#section-10.12)
- [RFC 7636: Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-wxw3-q3m9-c3jr
- https://github.com/better-auth/better-auth/issues/8897
- https://github.com/better-auth/better-auth/pull/8949
- https://github.com/better-auth/better-auth/commit/9deb7936aba7931f2db4b460141f476508f11bfd
- https://github.com/better-auth/better-auth
