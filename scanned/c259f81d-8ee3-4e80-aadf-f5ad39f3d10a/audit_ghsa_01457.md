# [M] Cross-Site Scripting in c3

## Summary
Severity: Medium
Advisory: GHSA-gvg7-pp82-cff3
CVE: CVE-2016-1000240
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-gvg7-pp82-cff3
Type: github-advisory

## Affected
- npm: `c3` — affected >=0 <0.4.11

## Details
Affected versions of `c3` are vulnerable to cross-site scripting via improper sanitization of HTML in rendered tooltips. 



## Recommendation

Update to 0.4.11 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000240
- https://github.com/c3js/c3/issues/1536
- https://github.com/c3js/c3/pull/1675
- https://github.com/c3js/c3/commit/de3864650300488a63d0541620e9828b00e94b42
- https://github.com/c3js/c3
- https://www.npmjs.com/advisories/138
