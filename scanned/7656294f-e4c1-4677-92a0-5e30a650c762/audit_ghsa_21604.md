# [M] TOCTOU Race Condition in Yarn

## Summary
Severity: Medium
Advisory: GHSA-hjxc-462x-x77j
CVE: CVE-2019-15608
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-hjxc-462x-x77j
Type: github-advisory

## Affected
- npm: `yarn` — affected >=0 <1.19.0

## Details
The package integrity validation in yarn < 1.19.0 contains a TOCTOU vulnerability where the hash is computed before writing a package to cache. It's not computed again when reading from the cache. This may lead to a cache pollution attack. This issue is fixed in 1.19.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15608
- https://github.com/yarnpkg/yarn/commit/0474b8c66a8ea298f5e4dedc67b2de464297ad1c
- https://hackerone.com/reports/703138
- https://github.com/yarnpkg/yarn/blob/master/CHANGELOG.md#1190
