# [M] @asymmetric-effort/specifyjs: CSS expression sanitization is bypassable in renderToString

## Summary
Severity: Medium
Advisory: GHSA-93q6-wwjh-jc6h
CVE: CVE-2026-50290
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-93q6-wwjh-jc6h
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/specifyjs` — affected >=0 <0.2.136

## Details
## Finding

**Location**: `core/src/server/render-to-string.ts:307-311`

CSS value sanitization stripped `expression(` and `url(javascript:` using simple regex, but could be bypassed with CSS unicode escapes (`\65xpression(`), null bytes, or CSS comments (`exp/**/ression(`).

**Mitigating Factor**: These CSS injection vectors only work in legacy browsers (IE6-IE10). SpecifyJS targets modern browsers.

## Status

**Fixed in v0.2.136** — CSS sanitization now normalizes unicode escapes and strips CSS comments before pattern matching. Also checks for `behavior:`, `-moz-binding`, and `-o-link` patterns.

## References
- https://github.com/asymmetric-effort/specifyjs/security/advisories/GHSA-93q6-wwjh-jc6h
- https://github.com/asymmetric-effort/specifyjs/commit/25d1fb491d99479efdf501f5f75e0bb80c908f0a
- https://github.com/asymmetric-effort/specifyjs
