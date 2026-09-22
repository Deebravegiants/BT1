# [H] Arbitrary JavaScript Execution in typed-function

## Summary
Severity: High
Advisory: GHSA-3qh4-r86r-grvm
CVE: CVE-2017-1001004
CWE: CWE-94
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-3qh4-r86r-grvm
Type: github-advisory

## Affected
- npm: `typed-function` — affected >=0 <0.10.6

## Details
Versions of `typed-function` prior to 0.10.6 are vulnerable to Arbitrary JavaScript Execution. Function names are not properly sanitized and may allow an attacker to execute arbitrary code.


## Recommendation

Upgrade to version 0.10.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1001004
- https://github.com/josdejong/typed-function/commit/6478ef4f2c3f3c2d9f2c820e2db4b4ba3425e6fe
- https://github.com/josdejong/typed-function/commit/6478ef4f2c3f3c2d9f2c820e2db4b4ba3425e6fe?diff=split#diff-9e1f22c2954a38db1fdf444dbc74e0a8
- https://github.com/josdejong/typed-function/blob/master/HISTORY.md#2017-11-18-version-0106
- https://snyk.io/vuln/SNYK-JS-TYPEDFUNCTION-174139
- https://www.npmjs.com/advisories/819
