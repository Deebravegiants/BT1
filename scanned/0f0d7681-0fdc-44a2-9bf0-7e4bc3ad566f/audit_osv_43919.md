# [C] phpMyFAQ before 4.1.7 Authentication Bypass via Tracking File

## Summary
Severity: Critical
Advisory: CVE-2026-75918
Aliases: GHSA-j5w2-cwwj-xj7x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-75918
Type: osv

## Details
phpMyFAQ before 4.1.7 stores password reset tokens in a publicly accessible tracking file when user tracking is enabled. Unauthenticated attackers can read the tracking file at content/core/data/trackingDDMMYYYY to extract reset tokens and replay them against the password reset API to take over user accounts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75918.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-j5w2-cwwj-xj7x
- https://nvd.nist.gov/vuln/detail/CVE-2026-75918
- https://www.vulncheck.com/advisories/phpmyfaq-before-authentication-bypass-via-tracking-file
