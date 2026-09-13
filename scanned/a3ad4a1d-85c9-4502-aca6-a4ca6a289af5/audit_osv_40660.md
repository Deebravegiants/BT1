# [M] LibreChat: 2FA Backup Code Regeneration Without OTP Verification Allows 2FA Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-54040
Aliases: GHSA-h59w-x9h4-m6gv
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54040
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.4-rc1, the POST /api/auth/2fa/backup/regenerate endpoint regenerates all 2FA backup codes without requiring any TOTP token or existing backup code verification. An attacker with a stolen session token can silently replace a victim's backup codes and use them to bypass 2FA login or disable 2FA entirely. This vulnerability is fixed in 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54040.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-h59w-x9h4-m6gv
- https://nvd.nist.gov/vuln/detail/CVE-2026-54040
