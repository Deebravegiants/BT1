# [H] phpMyFAQ before 4.1.7 2FA Brute-Force via Session-Scoped Throttle

## Summary
Severity: High
Advisory: CVE-2026-76213
Aliases: GHSA-f98m-hcjv-7rp9
CVSS: 7.5 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76213
Type: osv

## Details
phpMyFAQ before 4.1.7 contains a brute-force vulnerability in the two-factor authentication step where the failure counter is session-scoped and reset on each successful password re-authentication. Attackers with a valid password can bypass the five-attempt limit by obtaining a fresh session cookie and repeatedly re-authenticating to reset the counter, enabling unbounded TOTP code guessing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76213.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-f98m-hcjv-7rp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-76213
- https://www.vulncheck.com/advisories/phpmyfaq-before-2fa-brute-force-via-session-scoped-throttle
