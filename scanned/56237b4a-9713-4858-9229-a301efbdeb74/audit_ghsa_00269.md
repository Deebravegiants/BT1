# [M] Arbitrary File Write via Archive Extraction in unzipper

## Summary
Severity: Medium
Advisory: GHSA-884w-698f-927f
CVE: CVE-2018-1002203
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-27
Source: https://github.com/advisories/GHSA-884w-698f-927f
Type: github-advisory

## Affected
- npm: `unzipper` — affected >=0 <0.8.13

## Details
Versions of `unzipper` before 0.8.13 are vulnerable to arbitrary file write when used to extract a specifically crafted archive that contains path traversal filenames (`../../file.txt` for example).


## Recommendation

Update to version 0.3.18 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002203
- https://github.com/ZJONSSON/node-unzipper/pull/59
- https://github.com/ZJONSSON/node-unzipper/commit/2220ddd5b58f6252069a4f99f9475441ad0b50cd
- https://hackerone.com/reports/362119
- https://github.com/advisories/GHSA-884w-698f-927f
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/npm:unzipper:20180415
- https://www.npmjs.com/advisories/680
