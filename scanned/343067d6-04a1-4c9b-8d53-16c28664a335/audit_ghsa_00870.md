# [H] Unauthorized File Access in atompm

## Summary
Severity: High
Advisory: GHSA-v86x-f47q-f7f4
CWE: CWE-200
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-v86x-f47q-f7f4
Type: github-advisory

## Affected
- npm: `atompm` — affected >=0 <0.8.2

## Details
Versions of `atompm` prior to 0.8.2 are vulnerable to Unauthorized File Access. The package fails to sanitize relative paths in the URL for file downloads, allowing attackers to download arbitrary files from the system.


## Recommendation

Upgrade to version 0.8.2 or later.

## References
- https://www.npmjs.com/advisories/959
