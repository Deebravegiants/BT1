# [M] Reflected XSS in SilverStripe

## Summary
Severity: Medium
Advisory: GHSA-qvrv-2x7x-78x2
CVE: CVE-2019-19325
CWE: CWE-78, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-02-24
Source: https://github.com/advisories/GHSA-qvrv-2x7x-78x2
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.5.0 <4.5.2
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.4.5

## Details
SilverStripe through 4.4.x before 4.4.5 and 4.5.x before 4.5.2 allows Reflected XSS on the login form and custom forms. Silverstripe Forms allow malicious HTML or JavaScript to be inserted through non-scalar FormField attributes, which allows performing XSS (Cross-Site Scripting) on some forms built with user input (Request data). This can lead to phishing attempts to obtain a user&amp;#39;s credentials or other sensitive user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19325
- https://github.com/silverstripe/silverstripe-framework/commit/49fda52b12ba59f0a04bcabf78425586a8779e89
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2019-19325.yaml
- https://www.silverstripe.org/download/security-releases/cve-2019-19325
