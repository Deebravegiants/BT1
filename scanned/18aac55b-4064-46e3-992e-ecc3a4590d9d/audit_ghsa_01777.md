# [M] Path Traversal in statics-server

## Summary
Severity: Medium
Advisory: GHSA-j27j-4w6m-8fc4
CVE: CVE-2019-15596
CWE: CWE-22
Ecosystem: npm
Published: 2020-03-31
Source: https://github.com/advisories/GHSA-j27j-4w6m-8fc4
Type: github-advisory

## Affected
- npm: `statics-server` — affected >=0

## Details
All versions of `statics-server` are vulnerable to Path Traversal. The package fails to limit access to files outside of the served folder through symlinks.


## Recommendation

No fix is currently available. Do not use `statics-server` in production or consider using an alternative module until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15596
- https://hackerone.com/reports/695416
- https://www.npmjs.com/advisories/1303
