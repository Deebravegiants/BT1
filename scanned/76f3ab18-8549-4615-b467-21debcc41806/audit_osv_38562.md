# [H] blueprintUE: Password Reset Tokens Have No Expiry Window

## Summary
Severity: High
Advisory: CVE-2026-40585
Aliases: GHSA-qr65-6vp8-whjf
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40585
Type: osv

## Details
blueprintUE is a tool to help Unreal Engine developers. Prior to 4.2.0, when a password reset is initiated, a 128-character CSPRNG token is generated and stored alongside a password_reset_at timestamp. However, the token redemption function findUserIDFromEmailAndToken() queries only for a matching email + password_reset token pair — it does not check whether the password_reset_at timestamp has elapsed any maximum window. A generated reset token is valid indefinitely until it is explicitly consumed or overwritten by a subsequent reset request. This vulnerability is fixed in 4.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40585.json
- https://github.com/blueprintue/blueprintue-self-hosted-edition/security/advisories/GHSA-qr65-6vp8-whjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-40585
