# [M] Insufficient Session Expiration in github.com/greenpau/caddy-security

## Summary
Severity: Medium
Advisory: GHSA-vp66-gf7w-9m4x
CVE: CVE-2024-21492
CWE: CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-17
Source: https://github.com/advisories/GHSA-vp66-gf7w-9m4x
Type: github-advisory

## Affected
- Go: `github.com/greenpau/caddy-security` — affected >=0

## Details
All versions of the package github.com/greenpau/caddy-security are vulnerable to Insufficient Session Expiration due to improper user session invalidation upon clicking the "Sign Out" button. User sessions remain valid even after requests are sent to /logout and /oauth2/google/logout. Attackers who gain access to an active but supposedly logged-out session can perform unauthorized actions on behalf of the user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21492
- https://github.com/greenpau/caddy-security/issues/272
- https://blog.trailofbits.com/2023/09/18/security-flaws-in-an-sso-plugin-for-caddy
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMGREENPAUCADDYSECURITY-5920787
- github.com/greenpau/caddy-security
