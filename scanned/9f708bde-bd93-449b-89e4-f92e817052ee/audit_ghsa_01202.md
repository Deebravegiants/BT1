# [M] SQL Injection in mysql

## Summary
Severity: Medium
Advisory: GHSA-fvq6-55gv-jx9f
CVE: CVE-2015-9244
CWE: CWE-89
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-fvq6-55gv-jx9f
Type: github-advisory

## Affected
- npm: `mysql` — affected >=0 <2.0.0-alpha8

## Details
Versions of `mysql` prior to 2.0.0-alpha8 are affected by a SQL Injection vulnerability in the `mysql.escape()` function, which does not properly escape object keys.


## Recommendation

Update to version 2.0.0-alpha8 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9244
- https://github.com/felixge/node-mysql/issues/342
- https://www.npmjs.com/advisories/66
