# [C] phpMyFAQ contains Weak Password Requirements

## Summary
Severity: Critical
Advisory: GHSA-2rr3-rv49-p42f
CVE: CVE-2022-3754
CWE: CWE-521
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-29
Source: https://github.com/advisories/GHSA-2rr3-rv49-p42f
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.1.8

## Details
phpMyFAQ prior to version 3.1.8 has Weak Password Requirements. Version 3.1.8 introduces an eight-character minimum password length.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3754
- https://github.com/thorsten/phpmyfaq/commit/d7a87d2646287828c70401ca8976ef531fbc77ea
- https://github.com/thorsten/phpmyfaq
- https://huntr.dev/bounties/f4711d7f-1368-48ab-9bef-45f32e356c47
