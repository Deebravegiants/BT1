# [H] phpMyFAQ before 4.1.7 2FA Bypass via Remember-Me Cookie

## Summary
Severity: High
Advisory: CVE-2026-76207
Aliases: GHSA-hvj7-4fmg-53cr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76207
Type: osv

## Details
phpMyFAQ before 4.1.7 contains a two-factor authentication bypass vulnerability where remember-me tokens are issued before 2FA verification completes. Attackers with valid credentials can obtain a remember-me cookie, skip the 2FA challenge, and replay the cookie to gain full authenticated access without second-factor verification.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76207.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-hvj7-4fmg-53cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-76207
- https://www.vulncheck.com/advisories/phpmyfaq-before-2fa-bypass-via-remember-me-cookie
