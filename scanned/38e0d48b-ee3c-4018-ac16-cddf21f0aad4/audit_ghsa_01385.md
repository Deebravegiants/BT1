# [H] Regular Expression Denial of Service in sql-injection

## Summary
Severity: High
Advisory: GHSA-hvxq-j2r4-4jm8
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-hvxq-j2r4-4jm8
Type: github-advisory

## Affected
- npm: `sql-injection` — affected >=0.0.0

## Details
All versions of `sql-injection` are vulnerable to Regular Expression Denial of Service. The package processes a request's body with regular expressions that may take exponentially longer to execute for large inputs.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1163
