# [M] Hono: Cookie helper does not sanitize sameSite and priority, allowing Set-Cookie injection

## Summary
Severity: Medium
Advisory: GHSA-3hrh-pfw6-9m5x
CVE: CVE-2026-47675
CWE: CWE-113, CWE-1287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-3hrh-pfw6-9m5x
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.21

## Details
### Summary

The `serialize()` function in `hono/cookie` validates `domain` and `path` options against characters that corrupt `Set-Cookie` header syntax (`;`, `\r`, `\n`), but does not apply the same validation to `sameSite` and `priority`. An application that passes user-controlled input into either option may produce a `Set-Cookie` response header containing attacker-chosen additional attributes.

### Details

When constructing a `Set-Cookie` header value, `serialize()` appends the `sameSite` and `priority` option values directly into the output string after a presentation-only transformation (capitalizing the first character). Although the TypeScript type signature constrains these options to specific string literals, that constraint is not enforced at runtime; any string value, including one containing `;` or line-feed characters, passes through unchanged.

The validation guard that rejects `;`, `\r`, and `\n` from `domain` and `path` is not applied to `sameSite` or `priority`. An application that passes a request-derived value to either option therefore provides an injection point into the header line.

This issue arises when an application passes user-controlled input to the `sameSite` or `priority` option of `setCookie()` or `serialize()`.

### Impact

An attacker who can control the `sameSite` or `priority` option value may inject additional attributes into a `Set-Cookie` response header.

This may lead to:

- Cookie attribute injection — overriding `Domain`, `Path`, `HttpOnly`, `Secure`, or `Max-Age` for the affected cookie
- HTTP response header injection on runtimes that do not strictly validate header values, enabling a second attacker-controlled `Set-Cookie` header in the same response

This issue affects applications that pass user-derived input into the `sameSite` or `priority` option of `hono/cookie` serialization functions.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-3hrh-pfw6-9m5x
- https://nvd.nist.gov/vuln/detail/CVE-2026-47675
- https://github.com/honojs/hono/commit/905aedbc20661e0e2fa378783a7ec44a5c3df43d
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.21
