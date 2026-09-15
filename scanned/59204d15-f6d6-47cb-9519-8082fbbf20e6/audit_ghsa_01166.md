# [M] Unintended Require in larvitbase-www

## Summary
Severity: Medium
Advisory: GHSA-88h9-fc6v-jcw7
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-88h9-fc6v-jcw7
Type: github-advisory

## Affected
- npm: `larvitbase-www` — affected >=0.0.0

## Details
All versions of `larvitbase-www` are vulnerable to an Unintended Require. The package exposes an API endpoint and passes a GET parameter unsanitized to an `require()` call. This allows attackers to execute any `.js` file in the same folder as the server is running.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://hackerone.com/reports/526258
- https://www.npmjs.com/advisories/1156
