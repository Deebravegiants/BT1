# [M] Information Disclosure in extension "femanager" (femanager)

## Summary
Severity: Medium
Advisory: CVE-2026-77135
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-77135
Type: osv

## Details
The extension's user detail view fails to verify that a requested user record matches the configured or logged-in target, allowing any visitor with access to the Detail or List plugin to retrieve another frontend user's profile data, including name, email, date of birth and address, by supplying an arbitrary user ID.

## References
- https://packagist.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77135.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77135
- https://typo3.org/security/advisory/typo3-ext-sa-2026-024
- https://github.com/in2code-de/femanager
