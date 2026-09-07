# [M] undici vulnerable to cookie attribute injection via unsanitized domain and unparsed setCookie fields

## Summary
Severity: Medium
Advisory: GHSA-v3r7-h72x-cjcm
CVE: CVE-2026-16729
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-v3r7-h72x-cjcm
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <6.28.0
- npm: `undici` — affected >=7.0.0 <7.29.0
- npm: `undici` — affected >=8.0.0 <8.9.0

## Details
## Impact

The `setCookie` function has two attribute injection paths. `validateCookieDomain` does not reject semicolons (`validateCookiePath` already does at 0x3B), so a `domain` value like `example.com; SameSite=None` lands verbatim as `Domain=example.com; SameSite=None`. The `unparsed` array's loop only checks each entry contains `=` and does not sanitize values, so an entry like `X-Custom=val; HttpOnly` lands unchanged, injecting `HttpOnly` without the caller setting `cookie.httpOnly = true`.

Applications that pass user-controlled input to these fields, typically multi-tenant or reverse-proxy servers that scope session cookies to a tenant-supplied domain, can have SameSite CSRF protections bypassed, `Secure` or `HttpOnly` forced or stripped, or the intended SameSite tier overridden.

## Patches

Patched in undici v6.28.0, v7.29.0, and v8.9.0.

## Workarounds

- Sanitize `domain` values against the RFC 1034 letter-digit-hyphen set before passing to `setCookie`.
- Do not pass user-controlled data to the `unparsed` field.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-v3r7-h72x-cjcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-16729
- https://github.com/nodejs/undici/commit/10d93fc332f2c8c161982dec3833201de29891b5
- https://github.com/nodejs/undici/commit/3bf91ddb493e853957f3a58e155326a668ab8aef
- https://github.com/nodejs/undici/commit/af7484043ee075a6f216da0ad77e1dac55199235
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v6.28.0
- https://github.com/nodejs/undici/releases/tag/v7.29.0
- https://github.com/nodejs/undici/releases/tag/v8.9.0
