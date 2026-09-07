# [M] CSRF token exposure in TYPO3 extension

## Summary
Severity: Medium
Advisory: GHSA-vpw5-grxx-v396
CVE: CVE-2021-36793
CWE: CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N/E:F/RL:O/RC:C (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-vpw5-grxx-v396
Type: github-advisory

## Affected
- Packagist: `lms/routes` — affected >=0 <2.1.1

## Details
When using the CsrfTokenViewHelper the extension discloses the user's session identifier to HTML output without processing of additional cryptographic hashing algorithms. This vulnerability cannot be exploited directly and occurs in combination with a chained attack - like for instance Cross Site Scripting  in the frontend output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36793
- https://github.com/Lacr1ma/routes
- https://typo3.org/security/advisory/typo3-ext-sa-2021-008
