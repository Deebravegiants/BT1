# [M] Improper Request Caching Lookup in the Auth0 Next.js SDK

## Summary
Severity: Medium
Advisory: GHSA-wcgj-f865-c7j7
CVE: CVE-2025-67490
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-wcgj-f865-c7j7
Type: github-advisory

## Affected
- npm: `@auth0/nextjs-auth0` — affected >=4.11.0 <4.11.2
- npm: `@auth0/nextjs-auth0` — affected >=4.12.0 <4.12.1

## Details
### Description
When using affected versions of the Next.js SDK, simultaneous requests on the same client may result in improper lookups in the TokenRequestCache for the request results.

### Am I Affected?
You are affected if you meet the following preconditions:
- Applications using the auth0/nextjs-auth0 SDK with a singleton client instance, versions 4.11.0, 4.11.1, and 4.12.0.

### Affected product and versions
Auth0/nextjs-auth0 v4.11.0, v4.11.1, and v4.12.0.

### Resolution
Upgrade Auth0/nextjs-auth0 version to v4.11.2 or v4.12.1

### Acknowledgements
Okta would like to thank Joshua Rogers (MegaManSec) for their discovery and responsible disclosure.

## References
- https://github.com/auth0/nextjs-auth0/security/advisories/GHSA-wcgj-f865-c7j7
- https://nvd.nist.gov/vuln/detail/CVE-2025-67490
- https://github.com/auth0/nextjs-auth0/commit/26cc8a7c60f4b134700912736f991a25bd6bbf0b
- https://github.com/auth0/nextjs-auth0
