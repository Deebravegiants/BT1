# [M] Open Redirect in apostrophe

## Summary
Severity: Medium
Advisory: GHSA-h97g-4mx7-5p2p
CWE: CWE-601
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-h97g-4mx7-5p2p
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0 <2.92.0

## Details
Versions of `apostrophe` prior to 2.92.0 are vulnerable to Open Redirect. The package redirected requests to third-party websites if escaped URLs followed by a trailing `/` were appended at the end.



## Recommendation

Update to version 2.92.0 or later.

## References
- https://github.com/apostrophecms/apostrophe/commit/1eba144bb82bd43dab72ce36cfbd593361b6d9b7
- https://github.com/apostrophecms/apostrophe
- https://snyk.io/vuln/SNYK-JS-APOSTROPHE-451089
- https://www.npmjs.com/advisories/1029
