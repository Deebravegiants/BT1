# [H] Better Auth: OAuth refresh-token rotation forks the token family on concurrent redemption

## Summary
Severity: High
Advisory: GHSA-392p-2q2v-4372
CVE: CVE-2026-53517
CWE: CWE-294, CWE-362, CWE-367, CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-392p-2q2v-4372
Type: github-advisory

## Affected
- npm: `@better-auth/oauth-provider` — affected >=1.6.0 <1.6.11
- npm: `better-auth` — affected >=1.4.8-beta.7 <1.6.0

## Details
### Am I affected?

Users are affected if all of the following are true:

- Their project depends on `@better-auth/oauth-provider` at a version `>= 1.6.0, < 1.6.11`, or uses the embedded plugin in `better-auth >= 1.4.8-beta.7, < 1.6.0`.
- At least one OAuth client served by their application's authorization server requests the `offline_access` scope, so refresh tokens are minted.
- Concurrent redemption of the same refresh token is reachable: an SPA shares one refresh token across browser tabs without a mutex, a mobile client retries after a transient failure, an attacker who has stolen a refresh token times two requests, or a service worker queues offline requests.

If developer applications do not request `offline_access` for any client, no refresh tokens are minted and they are not exposed.

Fix:

1. Upgrade to `@better-auth/oauth-provider@1.6.11` or later.
2. If developers cannot upgrade, see workarounds below.

### Summary

The OAuth provider's `POST /oauth2/token` endpoint, on the `refresh_token` grant, performs a non-atomic read / validate / revoke / mint sequence on the `oauthRefreshToken` row. Two concurrent requests presenting the same parent refresh token both pass the revocation check before either revoke completes, so each mints a fresh refresh token. The replay-detection branch only fires when `revoked` is already truthy at read time, which is exactly the state concurrent attackers race past. The result is a forked refresh-token family from a single parent token.

### Details

The `adapter.update` predicate on the parent row is keyed on `id` only; it does not include `revoked IS NULL`, so two concurrent updates both succeed (last-write-wins, no error path). The schema does not declare `unique` on `oauthRefreshToken.token`, so concurrent creates do not collide on a unique-key violation either.

RFC 9700 §4.14 (OAuth Security Best Current Practice) prescribes refresh-token family invalidation on detected reuse; this implementation tries to enforce that contract through the `revoked` check, but the check is not atomic with the consumption step. Token rotation issues a new refresh token with each call, so a single stolen refresh token grants indefinite access until the row is revoked or its `refreshTokenExpiresAt` (default 7 days) passes. Rotation refreshes that window each call.

The fix lands an atomic compare-and-swap on the parent row inside the rotation primitive (`UPDATE ... WHERE id = ? AND revoked IS NULL` with a rowcount check), so the losing rotation fails closed with `invalid_grant` and the parent row stays marked revoked. Subsequent replay of the original refresh token then trips the existing family-invalidation guard. The schema gains a unique constraint on `oauthRefreshToken.token` for parity with `oauthAccessToken.token`.

### Patches

Fixed in `@better-auth/oauth-provider@1.6.11`. The refresh-token rotation primitive now performs an atomic compare-and-swap on the parent row, and the explicit `revokeRefreshToken` path uses the same CAS. On a contested rotation, exactly one caller wins and mints a fresh refresh token; the loser receives `invalid_grant`. Subsequent replay of the original refresh token trips the existing family-invalidation guard because the parent row stays marked revoked.

`@better-auth/memory-adapter@1.6.11` ships a compatibility fix in the same wave: the in-memory `where` clause now treats `undefined` and `null` as equivalent under an `eq null` predicate, mirroring SQL `IS NULL` and Mongo's missing-or-null semantics. Without this change, the CAS predicate `WHERE revoked IS NULL` falls through on every call against a row whose optional `revoked` field is absent (the adapter factory's `transformInput` skips writing `undefined` when no default exists), so the rotation above is broken for any deployment using the in-memory adapter.

Strict refresh-token family invalidation on a contested rotation, per RFC 9700 §4.14 (which calls for invalidating the winner's tokens too when reuse is detected at rotation time), is deferred to a follow-up minor on the `next` channel. Closing it cleanly requires an opt-in transactional rotation in the adapter contract so the family-delete cannot interleave with the winner's in-flight access-token insert. The deferred site carries a `FIXME(strict-family-invalidation)` marker.

Schema-migration note: the better-auth migration generator only emits `UNIQUE` for newly-created columns. Existing installs will not pick up the new `oauthRefreshToken.token` unique constraint from `migrate` / `generate`; add it manually if an application's operational tooling depends on it (`CREATE UNIQUE INDEX oauth_refresh_token_token_uniq ON "oauthRefreshToken" (token);`). The CAS fix above does not depend on the database-level constraint to be correct; the constraint is defense-in-depth so collisions from a buggy custom `generateRefreshToken` callback fail loudly.

### Workarounds

None of these close the bug fully without a code patch.

- **Adapter-level**: configure the database adapter to run the OAuth refresh handler under serializable isolation, or wrap the `adapter.update` on `oauthRefreshToken` with a row-level pessimistic lock (`SELECT ... FOR UPDATE`). Narrows the window without closing it.
- **Token lifetime**: pass `oauthProvider({ refreshTokenExpiresIn: 60 })` to expire forked families within one minute. Trades attacker persistence for shorter user sessions.
- **Client-side single-flight**: serialize refresh-token usage in the client SDK with a mutex. Mitigates honest concurrency but does nothing against an attacker with a stolen refresh token.
- **Disable refresh tokens**: do not request the `offline_access` scope. Closes the surface but breaks long-lived sessions.

### Impact

- **Indefinite access from a single stolen refresh token**: forked refresh-token families grant access at the original user's authorization scope, surviving past any single revocation if an attacker holds any branch.
- **Detection bypass**: legitimate users whose refresh token has been forked do not trip family invalidation when they refresh, because the attacker's branch already swapped the parent row out from under the legitimate user's check.

### Credit

Reported by @chdanielmueller.

### Resources

- [CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization (Race Condition)](https://cwe.mitre.org/data/definitions/362.html)
- [CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition](https://cwe.mitre.org/data/definitions/367.html)
- [CWE-294: Authentication Bypass by Capture-replay](https://cwe.mitre.org/data/definitions/294.html)
- [CWE-613: Insufficient Session Expiration](https://cwe.mitre.org/data/definitions/613.html)
- [RFC 9700 §4.14: Refresh Token Protection](https://datatracker.ietf.org/doc/html/rfc9700#section-4.14)
- [RFC 6749 §6: Refreshing an Access Token](https://datatracker.ietf.org/doc/html/rfc6749#section-6)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-392p-2q2v-4372
- https://nvd.nist.gov/vuln/detail/CVE-2026-53517
- https://github.com/better-auth/better-auth/commit/c6918ecc9e3a75892169415d7f6c95b591b6a52d
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.0
- https://github.com/better-auth/better-auth/releases/tag/v1.6.11
