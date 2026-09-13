# [M] grunt-gh-pages before 0.10.0 may allow unencrypted GitHub credentials to be written to a log file

## Summary
Severity: Medium
Advisory: GHSA-rrj3-qmh8-72pf
CVE: CVE-2016-10526
CWE: CWE-391
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-rrj3-qmh8-72pf
Type: github-advisory

## Affected
- npm: `grunt-gh-pages` — affected >=0 <0.10.0

## Details
Versions of `grunt-gh-pages` prior to 0.10.0 are affected by a vulnerability which may cause unencrypted GitHub credentials to be written to a log file in certain circumstances.

In the `grunt-gh-pages` deployment scenario where authentication is performed by injecting a GitHub token directly into the auth portion of the URL, `grunt-gh-pages` will write the token to a log file, unencrypted.


## Recommendation

Update to version 0.10.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10526
- https://github.com/tschaub/grunt-gh-pages/pull/41
- https://github.com/tschaub/grunt-gh-pages/pull/41/commits/590f69767203d8c379fe18cded93bd5ad6cb53cb
- https://github.com/tschaub/grunt-gh-pages/commit/2d277e3e969ccd4c2d493f3795400fa77e6b6342
- https://github.com/tschaub/grunt-gh-pages
- https://www.npmjs.com/advisories/85
