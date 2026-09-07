# [M] Comments plugin stored Cross-site Scripting (XSS) via an asset volume name

## Summary
Severity: Medium
Advisory: GHSA-69ww-wv3j-mhg4
CVE: CVE-2020-13870
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-69ww-wv3j-mhg4
Type: github-advisory

## Affected
- Packagist: `verbb/comments` — affected >=0 <1.5.5

## Details
An issue was discovered in the Comments plugin before 1.5.5 for Craft CMS. There is stored XSS via an asset volume name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13870
- https://github.com/verbb/comments
- https://github.com/verbb/comments/blob/craft-3/CHANGELOG.md#155---2020-05-28-critical
