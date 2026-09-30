# [M] Auth0 Symfony SDK Accepted Bearer Tokens via URL Query Parameter

## Summary
Severity: Medium
Advisory: GHSA-ffq7-hh2j-r24p
CVE: CVE-2026-50157
CWE: CWE-200, CWE-598
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-ffq7-hh2j-r24p
Type: github-advisory

## Affected
- Packagist: `auth0/symfony` — affected >=5.0.0-BETA0 <5.9.0

## Details
### Description
Applications built with the Auth0 Symphony SDK, using the Authorizer security authenticator to protect HTTP routes may accept OAuth 2.0 bearer access tokens provided through a URL query parameter, in addition to the standard Authorization header, which may increase the risk of access token exposure and replay against protected API endpoints.

### Resolution
Upgrade auth0/symfony to version 5.9.0 or greater.

### Acknowledgement
Okta would like to thank Alex Yeara for their discovery.

## References
- https://github.com/auth0/symfony/security/advisories/GHSA-ffq7-hh2j-r24p
- https://github.com/auth0/symfony/commit/172d1d3e0b9d1e93610d786118389a811179bc8a
- https://github.com/auth0/symfony/commit/bd1851b14ae15e99cbe87c96496cf25da025288a
- https://github.com/auth0/symfony
- https://github.com/auth0/symfony/releases/tag/5.9.0
