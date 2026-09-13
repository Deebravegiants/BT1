# [M] NocoDB's Refresh Tokens Not Revoked on Password Reset

## Summary
Severity: Medium
Advisory: GHSA-x4vh-j75g-268g
CVE: CVE-2026-28396
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-x4vh-j75g-268g
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <0.301.3

## Details
### Summary
The password reset flow did not revoke existing refresh tokens, allowing an attacker with a previously stolen refresh token to continue minting valid JWTs after the victim resets their password.

### Details
`passwordReset()` in `users.service.ts` updated `token_version` (invalidating JWTs) but did not call `UserRefreshToken.deleteAllUserToken()`. The `refreshToken()` method only checked token existence, not `token_version`. Both `passwordChange()` and `signOut()` correctly deleted all refresh tokens.

### Impact
An attacker who previously obtained a refresh token retains access after password reset until the token expires.

### Credit
This issue was reported by [@bugbunny-research](https://github.com/bugbunny-research) (bugbunny.ai).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-x4vh-j75g-268g
- https://nvd.nist.gov/vuln/detail/CVE-2026-28396
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/0.301.3
