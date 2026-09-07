# [H] phpMyFAQ vulnerable to Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-6rj8-9cm9-6gff
CVE: CVE-2022-3608
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-6rj8-9cm9-6gff
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.2.0-alpha
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <3.2.0-alpha

## Details
phpMyFAQ versions 3.1.7 and prior are vulnerable to stored cross-site scripting (XSS). A patch is available on the `main` branch of the repository and anticipated to be part of version 3.2.0-alpha.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3608
- https://github.com/thorsten/phpmyfaq/commit/37123edd50f854bd141e6fbe65221af2d5cf2677
- https://github.com/thorsten/phpMyFAQ
- https://huntr.dev/bounties/8f0f3635-9d81-4c55-9826-2ba955c3a850
