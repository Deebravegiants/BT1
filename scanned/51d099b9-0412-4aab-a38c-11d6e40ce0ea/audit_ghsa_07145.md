# [H] Auth.js: getToken() throws an uncaught exception on malformed Bearer authorization headers

## Summary
Severity: High
Advisory: GHSA-xmf8-cvqr-rfgj
CVE: CVE-2026-73418
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-23
Source: https://github.com/advisories/GHSA-xmf8-cvqr-rfgj
Type: github-advisory

## Affected
- npm: `@auth/core` — affected >=0.1.0 <0.41.3
- npm: `next-auth` — affected >=5.0.0-beta.0 <5.0.0-beta.32
- npm: `next-auth` — affected >=4.0.6 <4.24.15

## Details
## Summary

The exported `getToken()` helper (`next-auth/jwt` and `@auth/core/jwt`) can throw an uncaught exception when it reads a malformed `Authorization: Bearer …` header. When no session cookie is present, `getToken()` URL-decodes the bearer value before validating it, and malformed percent-encoding causes the decode step to throw rather than being treated as an invalid token. Because `getToken()` is commonly called in API routes, middleware, and other request handlers, a single unauthenticated request can trigger an unhandled exception in code paths that authenticate requests.

## Am I affected?

You are affected if **all** of the following hold:

- You use `next-auth` `<= 5.0.0-beta.25` (or `@auth/core` exposing the same `getToken()` implementation).
- Your application calls `getToken()` directly — for example in a Route Handler, middleware, or server-side request handler.
- You do not wrap that `getToken()` call in your own `try/catch`.

You are **not** affected if you only use the framework's `auth()` helper and never call `getToken()` yourself, or if every `getToken()` call site already has its own exception handling.

## Impact

- Denial of service: an unauthenticated request carrying a malformed Bearer authorization header can raise an unhandled exception in any handler that calls `getToken()`.
- The impact is per-request and limited to availability; it does not expose tokens, sessions, or other data, and does not bypass authentication.

CWE-20: Improper Input Validation.

## Patched version

The fix makes `getToken()` treat a malformed Bearer value as an invalid token and return `null`, matching how other undecodable tokens are already handled. Upgrade to the first release containing this fix (to be published; this advisory will be updated with the exact patched version before publication) and no code changes are required.

## Workarounds

If you cannot upgrade immediately, either:

- **Config/code-level:** wrap your `getToken()` calls so a thrown error is treated as "no token", e.g.

  ```ts
  let token = null
  try {
    token = await getToken({ req, secret })
  } catch {
    token = null
  }
  ```

- Or strip/normalize the incoming `Authorization` header at the edge (proxy, middleware) before it reaches `getToken()`, rejecting values whose Bearer portion is not valid percent-encoding.

## Credit

Reported by @deprrous. Thank you for the responsible disclosure.

## References
- https://github.com/nextauthjs/next-auth/security/advisories/GHSA-xmf8-cvqr-rfgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-73418
- https://github.com/nextauthjs/next-auth/pull/13467
- https://github.com/nextauthjs/next-auth/pull/13469
- https://github.com/nextauthjs/next-auth/commit/5bca2399a79ba8d116ca5179b4b1ebcd152e7f05
- https://github.com/nextauthjs/next-auth/commit/e707770f00c52b3479e43422b0200b059149ed53
- https://github.com/nextauthjs/next-auth
- https://github.com/nextauthjs/next-auth/releases/tag/@auth/core@0.41.3
- https://github.com/nextauthjs/next-auth/releases/tag/next-auth@4.24.15
- https://github.com/nextauthjs/next-auth/releases/tag/next-auth@5.0.0-beta.32
