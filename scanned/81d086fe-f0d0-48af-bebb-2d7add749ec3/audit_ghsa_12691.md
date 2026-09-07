# [M] phpMyFAQ Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-v6g2-jwrm-h5r5
CVE: CVE-2023-3469
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-v6g2-jwrm-h5r5
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <3.2.0-beta.2

## Details
phpMyFAQ prior to 3.2.0-beta.2 contains a cross-site scripting vulnerability. When an administrator restores a backup from a file, it's possible to trigger an error with a specially crafted file that can be displayed on the web page. Since the error message contains the invalid part of the file, any JavaScript code in the file is executed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3469
- https://github.com/thorsten/phpmyfaq/commit/04a0183c25dd425f4c2bfb5f75b7650b932ae278
- https://github.com/thorsten/phpMyFAQ
- https://huntr.dev/bounties/3565cfc9-82c4-4db8-9b8f-494dd81b56ca
