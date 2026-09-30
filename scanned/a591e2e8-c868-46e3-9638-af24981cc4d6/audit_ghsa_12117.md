# [M] Hono Vulnerable to Cookie Attribute Injection via Unsanitized domain and path in setCookie()

## Summary
Severity: Medium
Advisory: GHSA-5pq2-9x2x-5p6w
CVE: CVE-2026-29086
CWE: CWE-1113, CWE-113
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-5pq2-9x2x-5p6w
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.4

## Details
## Summary

The `setCookie()` utility did not validate semicolons (`;`), carriage returns (`\r`), or newline characters (`\n`) in the `domain` and `path` options when constructing the `Set-Cookie` header.

Because cookie attributes are delimited by semicolons, this could allow injection of additional cookie attributes if untrusted input was passed into these fields.

## Details

`setCookie()` builds the `Set-Cookie` header by concatenating option values. While the cookie value itself is URL-encoded, the `domain` and `path` options were previously interpolated without rejecting unsafe characters.

Including `;`, `\r`, or `\n` in these fields could result in unintended additional attributes (such as `SameSite`, `Secure`, `Domain`, or `Path`) being appended to the cookie header.

Modern runtimes prevent full header injection via CRLF, so this issue is limited to attribute-level manipulation within a single `Set-Cookie` header.

The issue has been fixed by rejecting these characters in the `domain` and `path` options.

## Impact

An attacker may be able to manipulate cookie attributes if an application passes user-controlled input directly into the `domain` or `path` options of `setCookie()`.

This could affect cookie scoping or security attributes depending on browser behavior. Exploitation requires application-level misuse of cookie options.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-5pq2-9x2x-5p6w
- https://nvd.nist.gov/vuln/detail/CVE-2026-29086
- https://github.com/honojs/hono/commit/44ae0c8cc4d5ab2bed529127a4ac72e1483ad073
- https://github.com/honojs/hono
