# [M] Denial of Service in handlebars

## Summary
Severity: Medium
Advisory: GHSA-f52g-6jhx-586p
CWE: CWE-400
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-f52g-6jhx-586p
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.4.5

## Details
Affected versions of `handlebars` are vulnerable to Denial of Service. The package's parser may be forced into an endless loop while processing specially-crafted templates. This may allow attackers to exhaust system resources leading to Denial of Service.


## Recommendation

Upgrade to version 4.4.5 or later.

## References
- https://www.npmjs.com/advisories/1300
