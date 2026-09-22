# [M] Hidden Directories Always Served in inert

## Summary
Severity: Medium
Advisory: GHSA-g4xp-36c3-f7mr
CVE: CVE-2014-10068
CWE: CWE-22
Ecosystem: npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-g4xp-36c3-f7mr
Type: github-advisory

## Affected
- npm: `inert` — affected >=0 <1.1.1

## Details
Versions 1.1.1 and earlier of `inert` are vulnerable to an information leakage vulnerability which causes files in hidden directories to be served, even when showHidden is false.

The inert directory handler always allows files in hidden directories to be served, even when `showHidden` is false.


## Recommendation

Update to version >= 1.1.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-10068
- https://github.com/hapijs/inert/pull/15
- https://github.com/hapijs/inert/commit/e8f99f94da4cb08e8032eda984761c3f111e3e82
- https://www.npmjs.com/advisories/14
