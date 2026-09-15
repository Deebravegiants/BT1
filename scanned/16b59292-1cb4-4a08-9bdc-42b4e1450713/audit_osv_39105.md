# [M] Vaultwarden: Refresh tokens not invalidated on security stamp rotation

## Summary
Severity: Medium
Advisory: CVE-2026-43911
Aliases: GHSA-6j4w-g4jh-xjfx
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-43911
Type: osv

## Details
Vaultwarden is a Bitwarden-compatible server written in Rust. Prior to 1.35.5, refresh tokens are not invalidated when the user's security_stamp is rotated by some security-sensitive operations (password change, KDF change, key rotation, email change, org admin password reset, emergency access takeover). This allows an attacker holding a previously obtained refresh token to maintain session access even after the user has taken action to secure their account. This vulnerability is fixed in 1.35.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43911.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-6j4w-g4jh-xjfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-43911
