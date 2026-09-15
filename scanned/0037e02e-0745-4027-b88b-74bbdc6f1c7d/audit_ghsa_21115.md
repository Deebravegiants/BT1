# [M] @ianwalter/merge Prototype Pollution via `merge` function

## Summary
Severity: Medium
Advisory: GHSA-42m6-g935-5vmq
CVE: CVE-2021-23397
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-42m6-g935-5vmq
Type: github-advisory

## Affected
- npm: `@ianwalter/merge` — affected >=0

## Details
All versions of package @ianwalter/merge are vulnerable to Prototype Pollution via the main (`merge`) function. @ianwalter/merge is [deprecated](https://github.com/ianwalter/merge/blob/master/README.md) and the maintainer suggests using [@generates/merger](https://github.com/generates/generates/tree/main/packages/merger) instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23397
- https://github.com/ianwalter/merge
- https://security.snyk.io/vuln/SNYK-JS-IANWALTERMERGE-1311022
