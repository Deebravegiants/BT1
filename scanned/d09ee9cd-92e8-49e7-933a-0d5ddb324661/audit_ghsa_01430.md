# [H] Cross-Site Scripting in markdown-to-jsx

## Summary
Severity: High
Advisory: GHSA-ccrp-c664-8p4j
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-ccrp-c664-8p4j
Type: github-advisory

## Affected
- npm: `markdown-to-jsx` — affected >=0 <6.11.4

## Details
Versions of `markdown-to-jsx` prior to 6.11.4 are vulnerable to Cross-Site Scripting. Due to insufficient input sanitization the package may render output containing malicious JavaScript. This vulnerability can be exploited through input of links containing `data` or VBScript URIs and a base64-encoded payload.


## Recommendation

Upgrade to version 6.11.4 or later.

## References
- https://github.com/probablyup/markdown-to-jsx/pull/307
- https://github.com/probablyup/markdown-to-jsx
- https://www.npmjs.com/advisories/1219
