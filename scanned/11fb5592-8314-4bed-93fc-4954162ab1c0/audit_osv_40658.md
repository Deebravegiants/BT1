# [M] LibreChat: 2FA Re-enrollment Allows Full Account 2FA Takeover Without OTP Verification

## Summary
Severity: Medium
Advisory: CVE-2026-54036
Aliases: GHSA-45fp-6q26-wfgq
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-54036
Type: osv

## Details
LibreChat is an enhanced ChatGPT clone that supports multiple AI providers. Prior to 0.8.4-rc1, the GET /api/auth/2fa/enable endpoint can be called by an authenticated user (or attacker with a stolen session) even when 2FA is already fully enabled on the account. This endpoint overwrites the existing TOTP secret, generates new backup codes, and sets twoFactorEnabled to false — all without requiring any TOTP or backup code verification. An attacker with a valid session token can completely take over a victim's 2FA, locking the legitimate user out of their own two-factor authentication. This vulnerability is fixed in 0.8.4-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54036.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-45fp-6q26-wfgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-54036
