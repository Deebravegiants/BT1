# [M] undici vulnerable to cross-user information disclosure via whitespace around equals in Cache-Control directives

## Summary
Severity: Medium
Advisory: GHSA-jr45-8vmc-qm54
CVE: CVE-2026-14643
CWE: CWE-436, CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-jr45-8vmc-qm54
Type: github-advisory

## Affected
- npm: `undici` — affected >=7.0.0 <7.29.0
- npm: `undici` — affected >=8.0.0 <8.9.0

## Details
## Impact

Undici's cache interceptor mishandles optional whitespace (OWS) placed around the `=` of a qualified `no-cache` or `private` Cache-Control directive, such as `no-cache ="authorization"` (OWS before `=`) or `no-cache= "authorization"` (OWS after `=`). The parser either drops the directive entirely or stores a field name with literal quote characters, so the downstream cache decisions do not recognize the qualification and the response is stored.

In shared-cache mode, this allows a response containing one user's authenticated data to be served from cache to a subsequent caller, including an unauthenticated caller, when both requests resolve to the same cache key. The impact class is identical to CVE-2026-9678 (GHSA-pr7r-676h-xcf6); this advisory covers the whitespace-around-`=` bypass that the earlier fix did not normalize.

Affected applications are those that explicitly enable the cache interceptor (`interceptors.cache()`) in shared mode, forward `Authorization` headers upstream, and receive cacheable responses with qualified `private` or `no-cache` directives whose field-name list is padded with OWS around the `=`.

## Patches

Upgrade to undici v7.29.0 or v8.9.0.

## Workarounds

If upgrade is not immediately possible, disable shared-cache mode for traffic that includes `Authorization` headers, avoid caching responses to authenticated requests, or add `Vary: Authorization` upstream.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-jr45-8vmc-qm54
- https://nvd.nist.gov/vuln/detail/CVE-2026-14643
- https://github.com/nodejs/undici/commit/85a240551c9feb8b8a0ecc56c84b2b3015add8a9
- https://github.com/nodejs/undici/commit/cb105d7c79069150982fa11acada0dd94a60dbbc
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v7.29.0
- https://github.com/nodejs/undici/releases/tag/v8.9.0
