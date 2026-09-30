# [M] Zitadel RefreshToken invalidation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6rrr-78xp-5jp8
CVE: CVE-2023-22492
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2023-01-11
Source: https://github.com/advisories/GHSA-6rrr-78xp-5jp8
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.17.0 <2.17.3
- Go: `github.com/zitadel/zitadel` — affected >=2.0.0 <2.16.4

## Details
### Impact
RefreshTokens is an OAuth 2.0 feature that allows applications to retrieve new access tokens and refresh the user's session without the need for interacting with a UI.

RefreshTokens were not invalidated when a user was locked or deactivated. The deactivated or locked user was able to obtain a valid access token only through a refresh token grant.

When the locked or deactivated user’s session was already terminated (“logged out”) then it was not possible to create a new session. Renewal of access token through a refresh token grant is limited to the configured amount of time (RefreshTokenExpiration).

### Patches
2.x versions are fixed on >= [2.17.3](https://github.com/zitadel/zitadel/releases/tag/v2.17.3)
2.16.x versions are fixed on >= [2.16.4](https://github.com/zitadel/zitadel/releases/tag/v2.16.4)

ZITADEL recommends upgrading to the latest versions available in due course.

### Workarounds
Ensure the RefreshTokenExpiration in the OIDC settings of your instance is set according to your security requirements.

### References

https://zitadel.com/docs/guides/manage/console/instance-settings#oidc-token-lifetimes-and-expiration

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-6rrr-78xp-5jp8
- https://nvd.nist.gov/vuln/detail/CVE-2023-22492
- https://github.com/zitadel/zitadel/commit/301e22c4956ead6014a8179463c37263f7301a83
- https://github.com/zitadel/zitadel/commit/fc892c52a10cd4ffdac395747494f3a93a7494c2
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.16.4
- https://github.com/zitadel/zitadel/releases/tag/v2.17.3
