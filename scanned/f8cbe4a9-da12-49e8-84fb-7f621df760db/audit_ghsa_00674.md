# [H] Cross-Site Scripting bypass in html-purify

## Summary
Severity: High
Advisory: GHSA-5p28-63mc-cgr9
CWE: CWE-79
Ecosystem: npm
Published: 2020-12-04
Source: https://github.com/advisories/GHSA-5p28-63mc-cgr9
Type: github-advisory

## Affected
- npm: `html-purify` — affected >=0

## Details
All versions of html-purify are vulnerable to cross-site scripting. The data attribute inside of object tags is not properly sanitized and allows javascript URIs leading to code execution.

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1586
