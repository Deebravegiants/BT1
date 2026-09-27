# [M] Directory Traversal in bitty

## Summary
Severity: Medium
Advisory: GHSA-f5mh-hq6h-whxv
CVE: CVE-2016-10561
CWE: CWE-22
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-f5mh-hq6h-whxv
Type: github-advisory

## Affected
- npm: `bitty` — affected >=0

## Details
Affected versions of `bitty` are vulnerable to directory traversal via the URL path in GET requests.


## Recommendation

The `bitty` package is not currently maintained, and has not seen an update since 2015. 

At this time, the best available mitigation is to use an alternative module that is actively maintained and provides similar functionality, such as [serve](https://www.npmjs.com/package/serve).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10561
- https://github.com/advisories/GHSA-f5mh-hq6h-whxv
- https://www.npmjs.com/advisories/150
