# [H] RCE via SSTI for users with permissions to access the Craft CMS Webhooks plugin

## Summary
Severity: High
Advisory: GHSA-8wg7-wm29-2rvg
CVE: CVE-2026-32261
CWE: CWE-1336
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-8wg7-wm29-2rvg
Type: github-advisory

## Affected
- Packagist: `craftcms/webhooks` — affected >=3.0.0 <3.2.0

## Details
The Webhooks plugin renders user-supplied template content through Twig’s `renderString()` function without sandbox protection. This allows an authenticated user with access to the Craft control panel and permissions to access the Webhooks plugin to inject Twig template code that calls arbitrary PHP functions.

This is possible even if `allowAdminChanges` is set to `false`.

Affected users should update to version 3.2.0 to mitigate the issue.

## References
- https://github.com/craftcms/webhooks/security/advisories/GHSA-8wg7-wm29-2rvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32261
- https://github.com/craftcms/webhooks/commit/88344991a68b07145567c46dfd0ae3328c521f62
- https://github.com/craftcms/webhooks
