# [C] Command Injection in marsdb

## Summary
Severity: Critical
Advisory: GHSA-5mrr-rgp6-x4gr
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-5mrr-rgp6-x4gr
Type: github-advisory

## Affected
- npm: `marsdb` — affected >=0.0.0

## Details
All versions of `marsdb` are vulnerable to Command Injection. In the `DocumentMatcher` class, selectors on `$where` clauses are passed to a Function constructor unsanitized. This allows attackers to run arbitrary commands in the system when the function is executed.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/bkimminich/juice-shop/issues/1173
- https://www.npmjs.com/advisories/1122
