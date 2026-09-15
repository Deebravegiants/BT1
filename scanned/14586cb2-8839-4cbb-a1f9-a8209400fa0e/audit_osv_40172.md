# [M] Snipe-IT: 2FA reset privilege bypass

## Summary
Severity: Medium
Advisory: CVE-2026-50550
Aliases: GHSA-6x4j-8954-5hxm
CVSS: 5.8 (CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-50550
Type: osv

## Details
Snipe-IT is an IT asset/license management system. Prior to 8.5.0, a user who can edit other users can reset a superadmin's two-factor authentication through app/Http/Controllers/Api/UsersController.php postTwoFactorReset(). The endpoint authorizes update access but does not enforce canEditAuthFields before clearing two_factor_secret and two_factor_enrolled. This issue is fixed in version 8.5.0.

## References
- https://github.com/grokability/snipe-it/releases/tag/v8.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50550.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-6x4j-8954-5hxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-50550
- https://github.com/grokability/snipe-it/commit/046ef82c6501be14df597f0bf5d0de2566c7d6bc
