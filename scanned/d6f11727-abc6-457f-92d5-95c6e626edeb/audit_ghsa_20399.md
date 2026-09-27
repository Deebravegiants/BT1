# [M] Improper Validation and Sanitization in url-parse

## Summary
Severity: Medium
Advisory: GHSA-46c4-8wrp-j99v
CVE: CVE-2020-8124
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-46c4-8wrp-j99v
Type: github-advisory

## Affected
- npm: `url-parse` — affected >=0.1.0 <1.4.5

## Details
Insufficient validation and sanitization of user input exists in url-parse npm package version 1.4.4 and earlier may allow attacker to bypass security checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8124
- https://github.com/github/advisory-database/pull/6762
- https://github.com/unshiftio/url-parse/commit/3ecd256f127c3ada36a84d9b8dd3ebd14316274b
- https://hackerone.com/reports/496293
- https://github.com/unshiftio/url-parse
