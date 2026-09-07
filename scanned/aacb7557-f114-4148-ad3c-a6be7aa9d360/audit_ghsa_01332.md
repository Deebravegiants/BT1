# [H] Cross-Site Scripting in mrk.js

## Summary
Severity: High
Advisory: GHSA-hpr5-wp7c-hh5q
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-hpr5-wp7c-hh5q
Type: github-advisory

## Affected
- npm: `mrk.js` — affected >=0 <2.0.1

## Details
Versions of `mrk.js` before 2.0.1 are vulnerable to cross-site scripting (XSS) when markdown is converted to HTML.


## Recommendation

Update to version 2.0.1 or later and use `mark.sanitizeURL()` for any `src` and `href` attributes when extending the markdown.

## References
- https://github.com/heyitsmeuralex/mrk/pull/3
- https://github.com/heyitsmeuralex/mrk
- https://www.npmjs.com/advisories/587
