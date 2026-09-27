# [M] undici vulnerable to cross-user information disclosure via shared cache whitespace bypass

## Summary
Severity: Medium
Advisory: GHSA-pr7r-676h-xcf6
CVE: CVE-2026-9678
CWE: CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-pr7r-676h-xcf6
Type: github-advisory

## Affected
- npm: `undici` — affected >=7.0.0 <7.28.0
- npm: `undici` — affected >=8.0.0 <8.5.0

## Details
## Impact

Undici's cache interceptor incorrectly classifies some responses as cacheable when the upstream `Cache-Control` header uses whitespace-padded qualified `private` or `no-cache` field names such as `private=" authorization"` or `no-cache="\tauthorization"`. The parser preserves the surrounding whitespace, so later comparisons against the literal `authorization` field name fail and the response is stored.

In shared-cache mode, this allows a response containing one user's authenticated data to be served from cache to a subsequent caller, including an unauthenticated caller, when both requests resolve to the same cache key.

Affected applications are those that explicitly enable the cache interceptor (`interceptors.cache()`) in shared mode, forward `Authorization` headers upstream, and receive cacheable responses with non-canonical qualified `private` or `no-cache` directives.

## Patches

Upgrade to undici v7.28.0 or v8.5.0.

## Workarounds

If upgrade is not immediately possible, disable shared-cache mode for traffic that includes `Authorization` headers, avoid caching responses to authenticated requests, or add `Vary: Authorization` upstream.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-pr7r-676h-xcf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-9678
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
