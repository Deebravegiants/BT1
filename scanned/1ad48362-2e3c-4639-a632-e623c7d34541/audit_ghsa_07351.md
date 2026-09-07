# [M] Hono: Server-Side XSS via JSX Escaping Bypass in cx() Utility

## Summary
Severity: Medium
Advisory: GHSA-w62v-xxxg-mg59
CVE: CVE-2026-59895
CWE: CWE-116, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-w62v-xxxg-mg59
Type: github-advisory

## Affected
- npm: `hono` — affected >=4.0.0 <4.12.27

## Details
### Summary

`cx()` in `hono/css` composes class names from plain strings but marks the result as already-escaped without HTML-escaping the input. When the result is used as a JSX `class` attribute during server-side rendering, the value is written into the attribute unescaped, so untrusted input can break out of the `class` attribute and inject arbitrary markup, leading to Cross-Site Scripting (XSS).

### Details

Because the composed value is treated as pre-escaped, the HTML attribute escaping normally applied to interpolated values is skipped, and characters such as `"` pass through unescaped — allowing a value to terminate the attribute and add further attributes or elements. This arises when an application passes untrusted, user-controlled input as a class name to `cx()`, for example when merging a base class with an externally provided `className`.

### Impact

During server-side rendering, an attacker who controls a value passed to `cx()` can inject arbitrary HTML into the page, resulting in stored or reflected XSS in the victim's browser.

This may lead to:

- Execution of attacker-controlled script in the victim's browser session.
- Session hijacking, credential theft, or actions performed on behalf of the victim.

Applications are affected only if they render JSX server-side and pass untrusted input as a class name to `cx()`.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-w62v-xxxg-mg59
- https://nvd.nist.gov/vuln/detail/CVE-2026-59895
- https://github.com/honojs/hono/commit/cd3f6f7194f0e5c9d4b26ae0cf232018d0f388fc
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.27
