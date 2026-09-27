# [M] thorsten/phpmyfaq vulnerable to improper access control

## Summary
Severity: Medium
Advisory: GHSA-2wjp-w7g7-h63q
CVE: CVE-2023-1883
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-2wjp-w7g7-h63q
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.1.12

## Details
thorsten/phpmyfaq prior to 3.1.12 is vulnerable to improper access control when FAQ News is marked as inactive in settings and have comments enabled, allowing comments to be posted on inactive FAQs. This has been fixed in 3.1.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1883
- https://github.com/thorsten/phpmyfaq/commit/db77df888178766987398597d4f153831c62a503
- https://github.com/thorsten/phpMyFAQ
- https://huntr.dev/bounties/2f1e417d-cf64-4cfb-954b-3a9cb2f38191
