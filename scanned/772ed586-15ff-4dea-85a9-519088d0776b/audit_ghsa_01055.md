# [H] Cross-Site Scripting (XSS) in pivottable

## Summary
Severity: High
Advisory: GHSA-cjj8-wfrx-jqcf
CVE: CVE-2016-1000241
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-cjj8-wfrx-jqcf
Type: github-advisory

## Affected
- npm: `pivottable` — affected >=1.4.0 <2.0.0

## Details
Affected versions of `pivottable` are vulnerable to cross-site scripting, due to a new mechanism used to render JSON elements.


## Recommendation

Update to version 2.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000241
- https://github.com/nicolaskruchten/pivottable/pull/401
- https://github.com/nicolaskruchten/pivottable
- https://www.npmjs.com/advisories/139
