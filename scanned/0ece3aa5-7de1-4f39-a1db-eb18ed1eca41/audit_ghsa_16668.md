# [M] ScnSocialAuth Cross-site Scripting vulnerability in login redirect param

## Summary
Severity: Medium
Advisory: GHSA-g6f5-4w43-2x63
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-29
Source: https://github.com/advisories/GHSA-g6f5-4w43-2x63
Type: github-advisory

## Affected
- Packagist: `socalnick/scn-social-auth` — affected >=0 <1.15.2

## Details
ScnSocialAuth version 1.15.2 has been released and includes a security for this vulnerability. Fix has been applied in https://github.com/SocalNick/ScnSocialAuth/commit/4a00966c41bc37251586d007564c5c891eba3700

### Affected versions
All versions below 1.15.2 are affected. dev-master is fixed starting from https://github.com/SocalNick/ScnSocialAuth/commit/4a00966c41bc37251586d007564c5c891eba3700

### Exploits
Because of missing escaping of the URL param redirect a XSS attack is possible.
For example: Setting the redirect param to `"><a%20href="http://github.com">GitHub.com</a><inpu%20type="hidden"%20"` would result in a link added to the login page.

### Resolution
If you are using any version of ScnSocialAuth below 1.15.2 please upgrade immediately by running composer update.

## References
- https://github.com/socalnick/scnsocialauth/issues/184
- https://github.com/SocalNick/ScnSocialAuth/commit/4a00966c41bc37251586d007564c5c891eba3700
- https://github.com/FriendsOfPHP/security-advisories/blob/master/socalnick/scn-social-auth/2015-01-15.yaml
- https://github.com/SocalNick/ScnSocialAuth/commit
