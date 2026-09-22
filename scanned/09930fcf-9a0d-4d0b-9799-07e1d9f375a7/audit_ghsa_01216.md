# [H] Denial of Service in serialize-to-js

## Summary
Severity: High
Advisory: GHSA-w5q7-3pr9-x44w
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-w5q7-3pr9-x44w
Type: github-advisory

## Affected
- npm: `serialize-to-js` — affected >=0 <2.0.0

## Details
Versions of `serialize-to-js` prior to 2.0.0 are vulnerable to Denial of Service. User input is not properly validated, allowing attackers to provide inputs that lead the execution to loop indefinitely.


## Recommendation

Upgrade to version 2.0.0 or later.

## References
- https://www.npmjs.com/advisories/790
