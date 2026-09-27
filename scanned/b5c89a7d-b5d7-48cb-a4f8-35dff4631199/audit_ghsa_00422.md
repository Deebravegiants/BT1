# [H] Regular Expression Denial of Service in negotiator

## Summary
Severity: High
Advisory: GHSA-7mc5-chhp-fmc3
CVE: CVE-2016-10539
CWE: CWE-400
Ecosystem: npm
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-7mc5-chhp-fmc3
Type: github-advisory

## Affected
- npm: `negotiator` — affected >=0 <0.6.1

## Details
Affected versions of `negotiator` are vulnerable to regular expression denial of service attacks, which trigger upon parsing a specially crafted `Accept-Language` header value.




## Recommendation

Update to version 0.6.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10539
- https://github.com/advisories/GHSA-7mc5-chhp-fmc3
- https://www.npmjs.com/advisories/106
