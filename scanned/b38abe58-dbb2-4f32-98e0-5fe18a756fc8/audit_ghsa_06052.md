# [M] Hono: ReDoS in CORS middleware via Access-Control-Request-Headers

## Summary
Severity: Medium
Advisory: GHSA-8j4g-w8fx-2239
CVE: CVE-2026-69207
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-8j4g-w8fx-2239
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.34

## Details
### Summary

The built-in CORS middleware (`hono/cors`) parses the attacker-controlled `Access-Control-Request-Headers` request header during a preflight (`OPTIONS`) request using a regular expression whose running time is quadratic in the input length. A single request carrying a long run of whitespace can consume seconds of CPU, and repeated requests can render the service unresponsive. This parsing runs under the default configuration.

### Details

On a CORS preflight, when `allowHeaders` is not configured - the default - the middleware reflects and parses the `Access-Control-Request-Headers` value. The parser used a whitespace-tolerant regular expression whose backtracking makes the work grow quadratically (O(n²)) with the length of the value when it contains a long whitespace sequence without a delimiter.

Because the header value is bounded only by the deployment's maximum HTTP header size, a single preflight can block request processing for a noticeable amount of time; on runtimes that share one execution thread across requests, this stalls concurrent requests as well. No authentication, special origin, or user interaction is required.

This issue arises for any application using `cors()` with the default (or an empty) `allowHeaders`. Applications that set a non-empty `allowHeaders` do not reach the affected path.

### Impact

An unauthenticated attacker can send preflight requests that each consume disproportionate CPU relative to their size, degrading or denying service. This is a denial-of-service issue only; it does not expose or modify data.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-8j4g-w8fx-2239
- https://github.com/honojs/hono/commit/93fc250d8b4df58ea542cb945171de8013d5e6d5
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.34
