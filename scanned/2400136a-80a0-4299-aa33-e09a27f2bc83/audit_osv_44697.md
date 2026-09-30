# [M] phpMyFAQ before 4.1.8 Authentication Bypass via Two-Factor Disable

## Summary
Severity: Medium
Advisory: CVE-2026-85590
Aliases: GHSA-h96g-59xp-7r5m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85590
Type: osv

## Details
phpMyFAQ before 4.1.8 contains an authentication bypass vulnerability in its two-factor authentication (TOTP) disable functionality. The removeTwofactorConfig() handler (reachable via POST /api/user/remove-twofactor) verifies only that the user is logged in and that a valid CSRF token is supplied, then disables TOTP without requiring password re-entry or a current TOTP code. The same downgrade is also reachable inline via PUT /api/user/data/update, which accepts a plain twofactor_enabled form field under the same session+CSRF-only guard. An attacker who has hijacked a user's session can silently strip two-factor protection from any account, including administrator accounts, after which password-only authentication succeeds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85590.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-h96g-59xp-7r5m
- https://nvd.nist.gov/vuln/detail/CVE-2026-85590
- https://www.vulncheck.com/advisories/phpmyfaq-before-4.1.8-authentication-bypass-via-two-factor-disable
