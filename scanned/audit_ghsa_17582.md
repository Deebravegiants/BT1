# [H] NextJS-Auth0 SDK Vulnerable to CDN Caching of Session Cookies

## Summary
Severity: High
Advisory: GHSA-f3fg-mf2q-fj3f
CVE: CVE-2025-48947
CWE: CWE-525
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-f3fg-mf2q-fj3f
Type: github-advisory

## Affected
- npm: `@auth0/nextjs-auth0` — affected >=4.0.1 <4.6.1

## Details
**Overview**
In Auth0 Next.js SDK versions 4.0.1 to 4.6.0, __session cookies set by auth0.middleware may be cached by CDNs due to missing Cache-Control headers.

**Am I Affected?**
You are affected by this vulnerability if you meet the following preconditions:

1. Applications using the NextJS-Auth0 SDK, versions between 4.0.1 to 4.6.0,
2. Applications using CDN or edge caching that caches responses with the Set-Cookie header.
3. If the Cache-Control header is not properly set for sensitive responses.

**Fix**
Upgrade auth0/nextjs-auth0 to v4.6.1.

## References
- https://github.com/auth0/nextjs-auth0/security/advisories/GHSA-f3fg-mf2q-fj3f
- https://nvd.nist.gov/vuln/detail/CVE-2025-48947
- https://github.com/auth0/nextjs-auth0/commit/12a62ca596db3b0827b39a4b865b882423e7cb1e
- https://github.com/auth0/nextjs-auth0
