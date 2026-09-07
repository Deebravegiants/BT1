# [H] Cross-Site Scripting in jingo

## Summary
Severity: High
Advisory: GHSA-mpjf-8cmf-p789
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-mpjf-8cmf-p789
Type: github-advisory

## Affected
- npm: `jingo` — affected >=0 <1.9.2

## Details
Versions of `jingo` prior to 1.9.2 are vulnerable to Cross-Site Scripting (XSS). If malicious input such as `<script>alert(1)</script>` is placed in the content of a wiki page, Jingo does not properly encode the input and it is executed instead of rendered as text.


## Recommendation

Upgrade to version 1.9.2

## References
- https://www.npmjs.com/advisories/750
