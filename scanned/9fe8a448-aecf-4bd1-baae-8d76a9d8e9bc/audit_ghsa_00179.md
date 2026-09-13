# [H] Regular Expression Denial of Service in parsejson

## Summary
Severity: High
Advisory: GHSA-q75g-2496-mxpp
CVE: CVE-2017-16113
CWE: CWE-400
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-q75g-2496-mxpp
Type: github-advisory

## Affected
- npm: `parsejson` — affected >=0

## Details
Affected versions of `parsejson` are vulnerable to a regular expression denial of service when parsing untrusted user input.


## Recommendation

The `parsejson` package has not been functionally updated since it was initially released.

Additionally, it provides functionality which is natively included in Node.js, and therefore the native `JSON.parse()` should be used, for both performance and security reasons.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16113
- https://github.com/get/parsejson/issues/4
- https://github.com/advisories/GHSA-q75g-2496-mxpp
- https://www.npmjs.com/advisories/528
