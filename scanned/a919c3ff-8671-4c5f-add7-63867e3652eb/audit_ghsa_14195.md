# [H] thorsten/phpmyfaq vulnerable to authentication bypass 

## Summary
Severity: High
Advisory: GHSA-4cr4-x82x-hwm9
CVE: CVE-2023-1886
CWE: CWE-294
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-4cr4-x82x-hwm9
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.1.12

## Details
thorsten/phpmyfaq prior to 3.1.12 is vulnerable to authentication bypass by capture-relay that allows unlimited comments to be sent. This has been fixed in 3.1.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1886
- https://github.com/thorsten/phpmyfaq/commit/27eaaae16850694634ac52416a0bd38b35d7330a
- https://github.com/thorsten/phpMyFAQ
- https://huntr.dev/bounties/b7d244b7-5ac3-4964-81ee-8dbb5bb5e33a
