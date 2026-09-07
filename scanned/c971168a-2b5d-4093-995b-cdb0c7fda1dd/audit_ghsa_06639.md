# [H] @better-auth/oauth-provider's OAuth authorization-code grant allows concurrent redemption when two token requests race the find-then-delete primitive

## Summary
Severity: High
Advisory: GHSA-7w99-5wm4-3g79
CVE: CVE-2026-53518
CWE: CWE-294, CWE-362, CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-7w99-5wm4-3g79
Type: github-advisory

## Affected
- npm: `@better-auth/oauth-provider` — affected >=1.6.0 <1.6.11
- npm: `better-auth` — affected >=0 <1.6.11

## Details
### Am I affected?

Users are affected if all of the following are true:

- Their project depends on `@better-auth/oauth-provider` at a version `>= 1.6.0, < 1.6.11`, or uses the embedded plugin in `better-auth >= 1.4.8-beta.7, < 1.6.0`, or enables the legacy `oidc-provider` or `mcp` plugins from `better-auth/plugins`.
- Their application exposes `/api/auth/oauth2/token` (or the legacy plugins' `/oauth2/token` and `/mcp/token`) as a token endpoint to OAuth/OIDC clients, including internal MCP clients (Claude Desktop, custom MCP tool callers, AI agents).
- Their application has not implemented an external mitigation: a load-balancer-level idempotency cache keyed by `code`, a database trigger that rejects duplicate token issuance for the same authorization code, or a custom adapter override that performs an atomic compare-and-delete.

Fix:

1. Upgrade to `@better-auth/oauth-provider@1.6.11` or later. If developers use the legacy plugin paths from `better-auth/plugins`, upgrade `better-auth` to `1.6.11` or later.
2. If developers cannot upgrade, see workarounds below.

### Summary

The OAuth provider's `POST /oauth2/token` endpoint, on the `authorization_code` grant, redeems a single-use authorization code through a non-atomic find-then-delete sequence. Two concurrent requests with the same `code` value both pass the read step before either delete completes, then both proceed to PKCE verification and `createUserTokens`. Each surviving request mints a fresh access token, refresh token, and id token. RFC 6749 §4.1.2 requires authorization codes to be single-use; this primitive does not enforce that under concurrency.

### Details

The same architectural primitive (find a single-use verification row, then delete it, then trust the row to authorize) is used in 20 other call sites across the codebase. The deletion primitive returns `Promise<void>`, discarding the row count surfaced by `adapter.deleteMany`, so no call site can detect "another caller already claimed this row". The fix lands at the primitive layer rather than at any individual call site.

The fix introduces a `claimVerificationByIdentifier` primitive at the internal-adapter layer that performs an atomic claim-and-return, replaces the find-then-delete pair at this call site, and migrates the highest-impact variant sites in the same release.

### Patches

Fixed in `@better-auth/oauth-provider@1.6.11` and `better-auth@1.6.11` for the legacy `oidc-provider` and `mcp` plugin paths. All three token-exchange call sites now consume the verification row through `internalAdapter.consumeVerificationValue`, an atomic claim primitive that deletes the row and returns its prior value in one operation. The first request to arrive takes the row and mints tokens; concurrent racers observe an empty result and return `invalid_grant`.

Error-code consistency is also tightened on the `@better-auth/oauth-provider` token endpoint: the malformed-verification-value branches previously returned a project-specific `invalid_verification` code, which is not part of RFC 6749 §5.2's response error set. Both branches now return `invalid_grant` so spec-compliant clients can branch on the standard code without a special case.

### Workarounds

None of these close the bug fully without a code patch. Upgrading is the only good path.

- **Network-layer**: deploy an authorization-server-aware reverse proxy (Envoy, NGINX with Lua, custom Cloudflare Worker) that holds an in-flight registry keyed by the `code` parameter and serializes concurrent requests for the same code. Fragile under multi-instance deployments unless the registry is shared (Redis-backed).
- **Database-layer**: add a SQL or Mongo uniqueness constraint that prevents two `oauthAccessToken` rows from being created with the same upstream code reference. Adapter-specific and not always feasible since the schema does not currently store the source code.
- **Application-layer**: wrap `deleteVerificationByIdentifier` with a custom hook that uses `adapter.deleteMany` and surfaces the count, then injects an `invalid_grant` rejection when the count is zero. Requires forking the internal adapter.

### Impact

- **Multiple independent token sets from a single authorization**: forked access tokens, refresh tokens, and id tokens issued from the same code, all valid for the original user's authorization scope.
- **Detection bypass**: standard OAuth single-use enforcement does not fire for the second redemption when both requests interleave through the read step.
- **Legacy-plugin reach**: `oidc-provider` and `mcp` plugins share the primitive on the same surface, so deployments using them inherit the same impact.

### Credit

Reported by @chdanielmueller.

### Resources

- [CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization (Race Condition)](https://cwe.mitre.org/data/definitions/362.html)
- [CWE-367: Time-of-check Time-of-use (TOCTOU) Race Condition](https://cwe.mitre.org/data/definitions/367.html)
- [CWE-294: Authentication Bypass by Capture-replay](https://cwe.mitre.org/data/definitions/294.html)
- [RFC 6749 §4.1.2: Authorization Response](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.2)
- [OAuth 2.1 §4.1: Authorization Code Grant](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1#section-4.1)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-7w99-5wm4-3g79
- https://nvd.nist.gov/vuln/detail/CVE-2026-53518
- https://github.com/better-auth/better-auth/commit/b4bc65a007784b2eb0efb459e5fa6fd8055d3ec9
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.11
