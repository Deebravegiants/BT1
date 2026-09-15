# [C] FreeScout's user invitation hash never expires: permanent unauthenticated account takeover if invite link leaks

## Summary
Severity: Critical
Advisory: CVE-2026-41902
Aliases: GHSA-hqff-cwx7-3jpm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-41902
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.217, the /user-setup/{hash} endpoint accepts a 60-character random invite_hash to set a new user's password. The endpoint performs no expiration check — the hash remains valid indefinitely until consumed. Combined with realistic hash-leakage scenarios (forwarded invite emails, HTTP referrer to external CDNs on the setup page, server-side log exposure, abandoned invite emails in shared inboxes), this enables unauthenticated permanent account takeover months or years after invite issuance. If the leaked invite was sent to an admin, the takeover yields admin access. This issue has been patched in version 1.8.217.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41902.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-hqff-cwx7-3jpm
- https://nvd.nist.gov/vuln/detail/CVE-2026-41902
