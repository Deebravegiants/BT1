# [M] NocoDB: Refresh Tokens Persist Through Password Recovery

## Summary
Severity: Medium
Advisory: GHSA-r989-7g3j-wjhw
CVE: CVE-2026-53928
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-r989-7g3j-wjhw
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0

## Details
### Summary
A stolen refresh token survived a password-forgot flow and could be used to mint fresh
JWTs even after the user reset their password.

### Details
`passwordChange` and `passwordReset` deleted the user's refresh tokens, but
`passwordForgot` only rotated `token_version` and revoked OAuth tokens — it did not
call `UserRefreshToken.deleteAllUserToken(user.id)`. An attacker holding a captured
refresh cookie could still exchange it for a new access token after the victim
triggered the recovery flow.

### Impact
Persistent unauthorized access after password recovery. Once a refresh token leaks, the
documented "Forgot password" recovery flow did not in fact revoke the attacker's
session.

### Credit
This issue was reported by [@bugbunny-research](https://github.com/bugbunny-research).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-r989-7g3j-wjhw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53928
- https://github.com/nocodb/nocodb
