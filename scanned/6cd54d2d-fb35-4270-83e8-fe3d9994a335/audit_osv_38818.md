# [H] Termix: Pending-TOTP temporary token can regenerate backup codes and neutralize TOTP

## Summary
Severity: High
Advisory: CVE-2026-42452
Aliases: GHSA-vx59-rf9w-9jv8
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42452
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to version 2.1.0, /users/login issues a temporary JWT (temp_token) for TOTP-enabled accounts. That token carries a pendingTOTP state and should only be valid for the second-factor flow. However, the auth middleware accepts this token on regular authenticated endpoints. This effectively turns 2FA into single-factor (password) for impacted accounts. This issue has been patched in version 2.1.0.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.1.0-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42452.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-vx59-rf9w-9jv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-42452
