# [M] Hono cache middleware ignores "Cache-Control: private" leading to Web Cache Deception

## Summary
Severity: Medium
Advisory: GHSA-6wqw-2p9w-4vw4
CVE: CVE-2026-24472
CWE: CWE-524, CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-6wqw-2p9w-4vw4
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.11.7

## Details
## Summary

Cache Middleware contains an information disclosure vulnerability caused by improper handling of HTTP cache control directives. The middleware does not respect standard cache control headers such as `Cache-Control: private` or `Cache-Control: no-store`, which may result in private or authenticated responses being cached and subsequently exposed to unauthorized users.

## Details

The vulnerability exists in the cache decision logic of Cache Middleware. When determining whether a response should be cached, the middleware does not take HTTP cache control semantics into account and may cache responses that are explicitly marked as private by the application. While some runtimes, such as Cloudflare Workers, enforce cache control restrictions at the platform level, other runtimes including Deno, Bun, and Node.js rely on the middleware’s behavior. As a result, applications running on these runtimes may unintentionally cache sensitive responses.

## Impact

This issue can lead to Web Cache Deception and information disclosure. If an authenticated user accesses an endpoint that returns user-specific or sensitive data and the response is cached despite being marked as private, subsequent unauthenticated requests may receive the cached response. This may result in the exposure of personally identifiable information or session-related data. The impact is limited to applications that use the hono/cache middleware and rely on it to correctly honor HTTP cache control directives.

## Affected Components

* Cache Middleware

## References
- https://github.com/honojs/hono/security/advisories/GHSA-6wqw-2p9w-4vw4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24472
- https://github.com/honojs/hono/commit/12c511745b3f1e7a3f863a23ce5f921c7fa805d1
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.11.7
