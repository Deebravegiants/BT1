# [H] Remote Code Execution in next

## Summary
Severity: High
Advisory: GHSA-5vj8-3v2h-h38v
CWE: CWE-20
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-5vj8-3v2h-h38v
Type: github-advisory

## Affected
- npm: `next` — affected >=0.9.9 <5.1.0

## Details
Versions of `next` prior to 5.1.0 are vulnerable to Remote Code Execution. The `/path:` route fails to properly sanitize input and passes it to a `require()` call. This allows attackers to execute JavaScript code on the server. Note that prior version 0.9.9 package `next` npm package hosted a different utility (0.4.1 being the latest version of that codebase), and this advisory does not apply to those versions.

## Recommendation

Upgrade to version 5.1.0.

## References
- https://github.com/vercel/next.js
- https://www.npmjs.com/advisories/1538
