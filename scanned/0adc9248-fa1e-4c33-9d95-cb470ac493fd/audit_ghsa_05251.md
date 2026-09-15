# [M] NocoDB: OAuth Tokens Persist Through Security Events

## Summary
Severity: Medium
Advisory: GHSA-g72g-r7m4-9x4g
CVE: CVE-2026-53926
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-g72g-r7m4-9x4g
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
OAuth access and refresh tokens were not revoked when the user changed, reset, or
recovered their password, leaving an attacker-issued OAuth grant valid after the user
believed they had locked the attacker out.

### Details
`revokeAllOAuthTokensByUser` in the users service was an empty stub being called from
`passwordChange`, `passwordForgot`, and `passwordReset`. It now delegates to
`OAuthToken.revokeAllByUser(userId)`, which deletes the rows and invalidates the
related auth caches. All three reset/recovery flows now consistently revoke refresh
tokens (GHSA-r989-7g3j-wjhw), OAuth tokens (this advisory), and rotate
`token_version`.

### Impact
Persistent unauthorized access through previously issued OAuth tokens after a
documented security event (password change, forgot, or reset).

### Credit
This issue was reported by [@bugbunny-research](https://github.com/bugbunny-research).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-g72g-r7m4-9x4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-53926
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
