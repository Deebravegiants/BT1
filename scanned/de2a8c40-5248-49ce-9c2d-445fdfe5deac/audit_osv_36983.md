# [C] FreeScout's Predictable Authentication Token Enables Account Takeover

## Summary
Severity: Critical
Advisory: CVE-2026-27637
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-27637
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.206, FreeScout's `TokenAuth` middleware uses a predictable authentication token computed as `MD5(user_id + created_at + APP_KEY)`. This token is static (never expires/rotates), and if an attacker obtains the `APP_KEY` — a well-documented and common exposure vector in Laravel applications — they can compute a valid token for any user, including the administrator, achieving full account takeover without any password. This vulnerability can be exploited on its own or in combination with CVE-2026-27636. Version 1.8.206 fixes both vulnerabilities.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27637.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-6gcm-v8xf-j9v9
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-mw88-x7j3-74vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27637
- https://github.com/freescout-help-desk/freescout/commit/004a8231f6e413af1d4680930b0e2342fd4283f9
