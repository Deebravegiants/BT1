# [C] Better Auth: OAuth refresh-token replay via missing client authentication on oidc-provider and mcp plugins

## Summary
Severity: Critical
Advisory: GHSA-pw9m-5jxm-xr6h
CVE: CVE-2026-53512
CWE: CWE-287, CWE-306, CWE-345, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-pw9m-5jxm-xr6h
Type: github-advisory

## Affected
- npm: `better-auth` — affected >=0 <1.6.11

## Details
### Am I affected?

Users are affected if all of the following are true:

- Their application uses `better-auth` and has enabled at least one of: `oidcProvider()` (imported from `better-auth/plugins/oidc-provider`), or `mcp()` (imported from `better-auth/plugins/mcp`).
- Their application has at least one confidential OAuth client registered (any client with `type: "web" | "native" | "user-agent-based"` in the `oauthApplication` table, or any `trustedClients` entry without `type: "public"`). Public clients with PKCE are not affected.
- Their application uses `better-auth` at a version below the patched release.

If an application only uses `@better-auth/oauth-provider` (the canonical replacement for `oidc-provider`) and the `mcp` plugin is not enabled, it is not affected.

Fix:

1. Upgrade to `better-auth@1.6.11` or later.
2. Migrate from the deprecated `oidcProvider()` to `@better-auth/oauth-provider` when feasible. The new package enforces client authentication on both grants by default.
3. If developers cannot upgrade their applications, see workarounds below.

### Summary

The legacy `oidcProvider` and `mcp` plugins each expose an OAuth 2.0 token endpoint whose `refresh_token` grant authenticates the request entirely on possession of the bound `refreshToken` row and a matching `client_id`. Neither plugin verifies the registered confidential client's `client_secret` on the refresh path. An attacker who obtains any valid `refresh_token` (via database read, log capture, browser-side XSS, or CORS-amplified script in the mcp case) and the public `client_id` can mint fresh access tokens and rotated refresh tokens until the chain is revoked.

### Details

RFC 6749 §6 and OAuth 2.1 §4.3 require confidential clients to authenticate to the token endpoint on every grant, including refresh. The same plugins' `authorization_code` grant correctly enforces `client_secret` (the oidc-provider via `verifyStoredClientSecret`, the mcp plugin via raw equality), which proves the omission on the refresh path is a regression rather than a design choice.

Token rotation issues a new `refresh_token` with each call, so a single leaked refresh-token grants indefinite access until the row is revoked or its `refreshTokenExpiresAt` (default 7 days) passes; rotation refreshes that window each call.

Two adjacent issues on the mcp surface ship in the same patch. The mcp `authorization_code` grant uses raw `===` for client-secret comparison and ignores the `storeClientSecret: "encrypted" | "hashed"` configuration; the fix routes both grants through `verifyStoredClientSecret`. The mcp `/mcp/token` endpoint sets `Access-Control-Allow-Origin: *` unconditionally, which amplifies the refresh bypass in browser contexts; the fix narrows the CORS allowlist.

The newer `@better-auth/oauth-provider` package routes both grants through `validateClientCredentials` and is not affected.

### Patches

Fixed in `better-auth@1.6.11`. The legacy `oidcProvider` and `mcp` token endpoints now require `client_secret` on the `refresh_token` grant for confidential clients, using the same constant-time comparison the `authorization_code` grant already used. Public clients are unaffected (they have no secret to enforce, and PKCE substitutes on the auth-code grant).

The `Authorization: Basic` parser is fixed to follow RFC 6749 §2.3.1: the credential is split on the first colon and each half is percent-decoded. Client IDs and secrets that contain reserved characters now authenticate correctly. The `/mcp/token` endpoint's CORS configuration is narrowed in the same change (the wildcard `Access-Control-Allow-Origin: *` header is removed), matching the standalone `@better-auth/oauth-provider` package.

The deprecated `oidc-provider` plugin remains deprecated. The recommended migration path is `@better-auth/oauth-provider`.

### Workarounds

None of these close the bug fully without a code patch.

- **Migrate to `@better-auth/oauth-provider`** if your deployment can adopt the new plugin. It enforces `client_secret` on both grants.
- **Force all clients to public + PKCE**: set every client's `type: "public"` and require PKCE. The bug is unreachable when there is no `client_secret` to verify.
- **Network-layer ingress restriction**: limit `/api/auth/oauth2/token` and `/api/auth/mcp/token` to known client IPs at the load balancer. Practical for server-to-server flows, not for end-user-device clients.
- **Out-of-band refresh-token rotation**: on any suspicion of leak, run `db.deleteMany({ model: "oauthAccessToken", where: [{ field: "clientId", value: <id> }] })` to invalidate all refresh tokens for the affected client.
- **For the mcp endpoint specifically**: drop the wildcard CORS at an upstream proxy and replace with a tight allowlist.

### Impact

- **Indefinite confidential-client impersonation**: an attacker holding any valid `refresh_token` and the public `client_id` can mint access tokens and rotated refresh tokens indefinitely, until the row is revoked. Rotation refreshes the expiration window each call.
- **Resource access at the user's authorized scope**: every minted access token carries the original user's authorization scope, so the attacker reads or writes whatever the resource server grants for that scope.

### Credit

Reported by @subhanUmer.

### Resources

- [CWE-306: Missing Authentication for Critical Function](https://cwe.mitre.org/data/definitions/306.html)
- [CWE-287: Improper Authentication](https://cwe.mitre.org/data/definitions/287.html)
- [CWE-345: Insufficient Verification of Data Authenticity](https://cwe.mitre.org/data/definitions/345.html)
- [CWE-863: Incorrect Authorization](https://cwe.mitre.org/data/definitions/863.html)
- [RFC 6749 §6: Refreshing an Access Token](https://datatracker.ietf.org/doc/html/rfc6749#section-6)
- [OAuth 2.1 §4.3: Refresh Token](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1#section-4.3)

## References
- https://github.com/better-auth/better-auth/security/advisories/GHSA-pw9m-5jxm-xr6h
- https://nvd.nist.gov/vuln/detail/CVE-2026-53512
- https://github.com/better-auth/better-auth/pull/9576
- https://github.com/better-auth/better-auth/commit/1f2ff4215c4affff0b140b0c0a712c0dde35659c
- https://github.com/better-auth/better-auth
- https://github.com/better-auth/better-auth/releases/tag/v1.6.11
