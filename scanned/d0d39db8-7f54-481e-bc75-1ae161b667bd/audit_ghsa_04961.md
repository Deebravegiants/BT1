# [M] undici vulnerable to HTTP header injection via Set-Cookie percent-decoding

## Summary
Severity: Medium
Advisory: GHSA-p88m-4jfj-68fv
CVE: CVE-2026-9679
CWE: CWE-93
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-p88m-4jfj-68fv
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.27.0
- npm: `undici` — affected >=7.0.0 <7.28.0
- npm: `undici` — affected >=8.0.0 <8.5.0

## Details
## Impact

undici's cookie parser in `parseSetCookie` percent-decodes cookie values via `qsUnescape`, turning encoded sequences like `%0D%0A`, `%00`, `%3B`, and `%3D` into their literal byte equivalents. RFC 6265 §5.4 does not specify any decoding and browsers do not decode either.

Applications that parse a `Set-Cookie` header and then forward the parsed value into a response header (proxies, middleware, SSR frameworks) become vulnerable to HTTP response header injection: an attacker-controlled upstream can inject arbitrary `Set-Cookie`, `Location`, or `Cache-Control` headers into the application's downstream response, enabling session fixation, open redirect, or cache poisoning.

Affected applications are those that use undici's cookie parsing (`parseSetCookie`, `parseCookie`, `getSetCookies`) and forward the parsed cookie value into a response header.

This was introduced in undici 7.0.0 via [#3789](https://github.com/nodejs/undici/pull/3789).

## Patches

Upgrade to undici v6.27.0, v7.28.0 or v8.5.0.

## Workarounds

If upgrade is not immediately possible, do not forward values returned by `parseSetCookie`/`parseCookie`/`getSetCookies` directly into response headers; sanitize the value first to strip or reject CR, LF, NUL, `;`, and `=` bytes.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-p88m-4jfj-68fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-9679
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
