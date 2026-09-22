# [M] phpMyFAQ before 4.1.8 Authentication Bypass via Unverified Password Change

## Summary
Severity: Medium
Advisory: CVE-2026-85591
Aliases: GHSA-6r2c-694w-24qv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85591
Type: osv

## Details
phpMyFAQ versions before 4.1.8 contain an authentication bypass vulnerability in the user control panel API endpoint that allows authenticated attackers to change account passwords without verifying the current password. Attackers with session access can submit a PUT request to the user data update endpoint with only a CSRF token to silently change any user's password, including administrators, causing irreversible account takeover and victim lockout.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85591.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-6r2c-694w-24qv
- https://nvd.nist.gov/vuln/detail/CVE-2026-85591
- https://www.vulncheck.com/advisories/phpmyfaq-before-4.1.8-authentication-bypass-via-unverified-password-change
