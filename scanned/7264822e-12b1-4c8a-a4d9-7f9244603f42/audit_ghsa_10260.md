# [M] Auth0 Next.js SDK has Improper Proxy Cache Lookup

## Summary
Severity: Medium
Advisory: GHSA-xq8m-7c5p-c2r6
CVE: CVE-2026-40155
CWE: CWE-362, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-xq8m-7c5p-c2r6
Type: github-advisory

## Affected
- npm: `@auth0/nextjs-auth0` — affected >=4.12.0 <4.18.0

## Details
### Description
In affected versions of the Next.js SDK, simultaneous requests that trigger a nonce retry may cause the proxy cache fetcher to perform improper lookups for the token request results.

### Which Projects are Affected?
Users are affected if they meet all of the following preconditions:
- Applications using the auth0/nextjs-auth0 SDK, versions 4.12.0 to 4.17.0, and
- Applications using the proxy handler  /me/* and /my-org/* with DPoP enabled.


### Affected product and versions
Auth0/nextjs-auth0 v4.12.0 to 4.17.0

### Resolution
Upgrade Auth0/nextjs-auth0 version to v4.18.0 or greater

### Acknowledgements
Okta would like to thank Reynaldo Immanuel for their discovery and responsible disclosure.

## References
- https://github.com/auth0/nextjs-auth0/security/advisories/GHSA-xq8m-7c5p-c2r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-40155
- https://github.com/auth0/nextjs-auth0/commit/98c36dc306970c2230ea1a32efef431d29b99978
- https://github.com/auth0/nextjs-auth0
- https://github.com/auth0/nextjs-auth0/releases/tag/v4.18.0
