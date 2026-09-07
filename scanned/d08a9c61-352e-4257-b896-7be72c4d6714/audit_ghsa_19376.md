# [M] Auth0 NextJS SDK v4 Missing Session Invalidation

## Summary
Severity: Medium
Advisory: GHSA-pjr6-jx7r-j4r6
CVE: CVE-2025-46344
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-pjr6-jx7r-j4r6
Type: github-advisory

## Affected
- npm: `@auth0/nextjs-auth0` — affected >=4.0.1 <4.5.1

## Details
### Overview
Auth0 NextJS `v4.0.1` to `v4.5.0` does not invoke `.setExpirationTime` when generating a JWE token for the session. As a result, the JWE does not contain an internal expiration claim. While the session cookie may expire or be cleared, the JWE remains valid.

### Am I Affected?
You are affected if you are using Auth0 NextJS SDK v4.

### Fix
Upgrade to `v4.5.1`.

## References
- https://github.com/auth0/nextjs-auth0/security/advisories/GHSA-pjr6-jx7r-j4r6
- https://nvd.nist.gov/vuln/detail/CVE-2025-46344
- https://github.com/auth0/nextjs-auth0/commit/a4f061aed02ffa132feca8adfbd11704df17e1c3
- https://github.com/auth0/nextjs-auth0
- https://github.com/auth0/nextjs-auth0/releases/tag/v4.5.1
