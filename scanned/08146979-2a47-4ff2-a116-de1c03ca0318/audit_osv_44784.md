# [C] Lara Dashboard before 1.3.0 Missing Authentication in screenshot-login Route

## Summary
Severity: Critical
Advisory: CVE-2026-86184
Aliases: GHSA-wj35-4h53-phfp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86184
Type: osv

## Details
Lara Dashboard before 1.3.0 contains an authentication bypass vulnerability in the screenshot-login route that allows unauthenticated attackers to authenticate as any user by email when APP_ENV is not production. Attackers can request the GET /screenshot-login/{email} endpoint with a registered email address to receive a fully authenticated session, enabling access to user administration, settings, database contents, and arbitrary code execution through the module installer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86184.json
- https://github.com/laradashboard/laradashboard/releases/tag/v1.3.0
- https://github.com/laradashboard/laradashboard/security/advisories/GHSA-wj35-4h53-phfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-86184
- https://www.vulncheck.com/advisories/lara-dashboard-before-1.3.0-missing-authentication-in-screenshot-login-route
- https://github.com/laradashboard/laradashboard/commit/50986e4ac58c883dd8f064cf32be3e2a87c11b24
- https://github.com/laradashboard/laradashboard
- https://github.com/laradashboard/laradashboard/blob/v1.2.2/app/Http/Controllers/Backend/Auth/ScreenshotGeneratorLoginController.php
