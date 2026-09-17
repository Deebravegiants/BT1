# [H] ReDoS via long UserAgent header in ua-parser

## Summary
Severity: High
Advisory: GHSA-pmg9-p9r2-6q87
CVE: CVE-2017-16086
CWE: CWE-400
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-pmg9-p9r2-6q87
Type: github-advisory

## Affected
- npm: `ua-parser` — affected >=0

## Details
Affected versions of `ua-parser` are vulnerable to regular expression denial of service when given a specially crafted `User-Agent` header.


## Recommendation

No patch is currently available for this vulnerability.

The best mitigation is currently to avoid using this package, using a different, functionally equivalent package such as [useragent](https://www.npmjs.com/package/useragent).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16086
- https://github.com/advisories/GHSA-pmg9-p9r2-6q87
- https://www.npmjs.com/advisories/316
