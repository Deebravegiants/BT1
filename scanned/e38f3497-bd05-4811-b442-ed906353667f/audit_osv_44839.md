# [H] Snipe-IT before 8.7.0 Authentication Bypass via API Middleware

## Summary
Severity: High
Advisory: CVE-2026-86762
Aliases: GHSA-cj4w-vx6j-42rf
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86762
Type: osv

## Details
Snipe-IT before 8.7.0 does not apply the CheckUserIsActivated middleware to the `api` middleware group in app/Http/Kernel.php, and deactivating a user does not revoke that user's Passport personal access tokens. As a result, although a deactivated account is correctly refused at web login, its existing API token continues to authenticate and to grant read and write access to the REST API (assets, users, licenses, etc.) at the account's prior permission level until the token expires. A deactivated account that retains user-management permissions can re-activate itself through the API, permanently defeating the deactivation control.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86762.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-cj4w-vx6j-42rf
- https://nvd.nist.gov/vuln/detail/CVE-2026-86762
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-authentication-bypass-via-api-middleware
- https://github.com/grokability/snipe-it/commit/b3f12f974bb2c0175ea68dad163ed04726db4280
