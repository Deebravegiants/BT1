# [M] phpMyFAQ contains a CSV injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x2v3-9p22-w3x6
CVE: CVE-2023-53929
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-18
Source: https://github.com/advisories/GHSA-x2v3-9p22-w3x6
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0

## Details
phpMyFAQ 3.1.12 contains a CSV injection vulnerability that allows authenticated users to inject malicious formulas into their profile names. Attackers can modify their user profile name with a payload like 'calc|a!z|' to trigger code execution when an administrator exports user data as a CSV file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-53929
- https://github.com/thorsten/phpMyFAQ
- https://www.exploit-db.com/exploits/51399
- https://www.phpmyfaq.de
- https://www.vulncheck.com/advisories/phpmyfaq-csv-injection-via-user-profile-export
