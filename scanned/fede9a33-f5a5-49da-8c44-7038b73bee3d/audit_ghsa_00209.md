# [H] Github Token Leak in aegir

## Summary
Severity: High
Advisory: GHSA-6xhf-x49c-m5m6
CVE: CVE-2017-16225
CWE: CWE-200
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-6xhf-x49c-m5m6
Type: github-advisory

## Affected
- npm: `aegir` — affected >=12.0.0 <12.0.8

## Details
Affected versions of `aegir` bundle and publish the current users github token to npm when `aegir-release` is executed.


## Recommendation

Update to version 12.0.8 or later.

If you used this module to do a release for your project you should invalidate the GitHub tokens that were leaked.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16225
- https://github.com/advisories/GHSA-6xhf-x49c-m5m6
- https://www.npmjs.com/advisories/546
