# [H] SQL Injection in Yeswiki

## Summary
Severity: High
Advisory: GHSA-xgx2-332h-9x6q
CVE: CVE-2021-43091
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-xgx2-332h-9x6q
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.1.0

## Details
An SQL Injection vlnerability exits in Yeswiki doryphore 20211012 via the email parameter in the registration form. The issue was fixed in Yeswiki version 4.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43091
- https://github.com/yeswiki/yeswiki/commit/c9785f9a92744c3475f9676a0d8f95de24750094
- https://github.com/yeswiki/yeswiki
- https://huntr.dev/bounties/07f245a7-ee9f-4b55-a0cc-13d5cb1be6e0
