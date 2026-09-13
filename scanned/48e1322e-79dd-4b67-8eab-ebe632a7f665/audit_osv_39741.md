# [H] Vaultwarden: SSO Email Auto-Link Can Bind an Existing Local Account to an Attacker-Controlled IdP Identity

## Summary
Severity: High
Advisory: CVE-2026-47164
Aliases: GHSA-6x5c-84vm-5j56
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-47164
Type: osv

## Details
Vaultwarden is a Bitwarden-compatible server written in Rust. Prior to 1.36.0, Vaultwarden's SSO login flow checked the IdP email_verified claim only for new-user creation and not when SSO_SIGNUPS_MATCH_EMAIL=true linked an IdP identity to an existing local account, allowing an attacker-controlled IdP identity asserting a victim email address to bind to and authenticate as that account. This issue is fixed in version 1.36.0.

## References
- https://github.com/dani-garcia/vaultwarden/releases/tag/1.36.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47164.json
- https://github.com/dani-garcia/vaultwarden/security/advisories/GHSA-6x5c-84vm-5j56
- https://nvd.nist.gov/vuln/detail/CVE-2026-47164
- https://github.com/dani-garcia/vaultwarden/commit/d297e274a35dccd0f5d935e9d5934e0f7e9c0a87
- https://github.com/dani-garcia/vaultwarden/pull/7163
