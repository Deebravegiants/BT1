# [M] Foundation Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p8pc-3f7w-jr5q
CVE: CVE-2020-26304
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-26
Source: https://github.com/advisories/GHSA-p8pc-3f7w-jr5q
Type: github-advisory

## Affected
- npm: `foundation-sites` — affected >=0

## Details
Foundation is a front-end framework. Versions 6.3.3 and prior contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS). As of time of publication, it is unknown if any fixes are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26304
- https://github.com/foundation/foundation-sites/issues/12180
- https://github.com/foundation/foundation-sites
- https://securitylab.github.com/advisories/GHSL-2020-290-redos-foundation-sites
