# [C] Arbitrary Code Execution in mathjs

## Summary
Severity: Critical
Advisory: GHSA-pv8x-p9hq-j328
CVE: CVE-2017-1001003
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-12-18
Source: https://github.com/advisories/GHSA-pv8x-p9hq-j328
Type: github-advisory

## Affected
- npm: `mathjs` — affected >=0 <3.17.0

## Details
math.js before 3.17.0 had an issue where private properties such as a constructor could be replaced by using unicode characters when creating an object.


## Recommendation

Upgrade to version 3.17.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1001003
- https://github.com/josdejong/mathjs/commit/a60f3c8d9dd714244aed7a5569c3dccaa3a4e761
- https://github.com/advisories/GHSA-pv8x-p9hq-j328
- https://github.com/josdejong/mathjs/blob/master/HISTORY.md#2017-11-18-version-3170
- https://www.npmjs.com/advisories/551
