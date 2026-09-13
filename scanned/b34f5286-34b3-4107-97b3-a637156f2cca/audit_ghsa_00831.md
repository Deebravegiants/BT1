# [M] Tracking Module in botbait

## Summary
Severity: Medium
Advisory: GHSA-4r5x-qjqc-p579
CVE: CVE-2017-16126
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-4r5x-qjqc-p579
Type: github-advisory

## Affected
- npm: `botbait` — affected >=0.0.0

## Details
The module `botbait` is a tool to be used to track bot and automated tools usage with-in the npm ecosystem.

`botbait` is known to record and track user information.

The module tracks the following information.
- Source IP
- process.versions
- process.platform
- How the module was invoked (test, require, pre-install)


## Recommendation

This package has no functional value, and should be removed from your environment if discovered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16126
- https://web.archive.org/web/20210120201359/https://www.npmjs.com/advisories/483
