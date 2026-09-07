# [M] Hono's Cache Middleware ignores Vary: Authorization / Vary: Cookie leading to cross-user cache leakage

## Summary
Severity: Medium
Advisory: GHSA-p77w-8qqv-26rm
CVE: CVE-2026-44457
CWE: CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-p77w-8qqv-26rm
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.18

## Details
### Summary

Cache Middleware does not skip caching for responses that declare per-user variance via `Vary: Authorization` or `Vary: Cookie`. As a result, a response cached for one authenticated user may be served to subsequent requests from different users.

### Details

The Cache Middleware skips caching when a response carries `Vary: *`, certain `Cache-Control` directives (`private`, `no-store`, `no-cache`), or `Set-Cookie`. However, `Vary: Authorization` and `Vary: Cookie` — the standard signals defined in RFC 9110 / RFC 9111 to indicate per-user responses — are not treated as cache-skip reasons.

This issue arises when applications use the Cache Middleware on endpoints that return user-specific data and rely on `Vary: Authorization` or `Vary: Cookie` to scope the response per user, without also setting `Cache-Control: private`.

### Impact

A user may receive a cached response that was originally generated for a different authenticated user. This may lead to:

- Disclosure of personally identifiable information or other user-specific data present in the response body
- Inconsistent or incorrect behavior in user-specific endpoints

This issue affects applications that use the Cache Middleware on endpoints whose responses vary by `Authorization` or `Cookie` and that do not also set `Cache-Control: private`.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-p77w-8qqv-26rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-44457
- https://github.com/honojs/hono
