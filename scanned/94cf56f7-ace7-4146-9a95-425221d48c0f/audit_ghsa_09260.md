# [M] Hono has CSS Declaration Injection via Style Object Values in JSX SSR

## Summary
Severity: Medium
Advisory: GHSA-qp7p-654g-cw7p
CVE: CVE-2026-44458
CWE: CWE-116, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-qp7p-654g-cw7p
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.18

## Details
### Summary

The JSX renderer escapes `style` attribute object values for HTML but not for CSS. Untrusted input in a `style` object value or property name can therefore inject additional CSS declarations into the rendered `style` attribute. The impact is limited to CSS and does not allow JavaScript execution or HTML attribute breakout.

### Details

`style` object values are serialized into a CSS declaration list and escaped for HTML attribute context only. Characters that act as CSS declaration boundaries — such as `;`, comment markers, quoted strings, and block delimiters — are valid in HTML attribute content and can extend a value beyond its assigned property.

This issue arises when untrusted input is interpolated into a JSX `style` object and rendered server-side.

### Impact

An attacker who can control the value or property name of a `style` object may inject arbitrary CSS declarations. This may lead to:

- Visual manipulation of the page, including full-viewport overlays usable for phishing
- Outbound requests to attacker-controlled hosts via CSS resource references such as `url(...)`
- Hijacking of UI affordances through layout, positioning, or visibility changes

This issue affects applications that render JSX on the server with `style` object values or property names derived from untrusted input.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-qp7p-654g-cw7p
- https://github.com/honojs/hono
