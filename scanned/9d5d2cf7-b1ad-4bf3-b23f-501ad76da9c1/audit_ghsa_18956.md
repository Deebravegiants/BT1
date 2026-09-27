# [H] authkit-nextjs may let session cookies be cached in CDNs

## Summary
Severity: High
Advisory: GHSA-p8pf-44ff-93gf
CVE: CVE-2025-64762
CWE: CWE-524
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-11-20
Source: https://github.com/advisories/GHSA-p8pf-44ff-93gf
Type: github-advisory

## Affected
- npm: `@workos-inc/authkit-nextjs` — affected >=0 <2.11.1

## Details
In `authkit-nextjs` version 2.11.0 and below, authenticated responses do not defensively apply anti-caching headers. In environments where CDN caching is enabled, this can result in session tokens being included in cached responses and subsequently served to multiple users.

Next.js applications deployed on Vercel are unaffected **unless** they manually enable CDN caching by setting cache headers on authenticated paths.

### Impact
This vulnerability may lead to session caching, potentially allowing unauthorized users to obtain another user’s session token. The severity depends on deployment configuration, caching policy, and whether authenticated routes are inadvertently cached.

### Patches
Patched in `authkit-nextjs` 2.11.1, which applies anti-caching headers to all responses behind authentication.

### Notes
Authentication middleware should set anti-caching headers for authenticated routes as a defense in depth measure, but cannot guarantee these headers will not be overwritten elsewhere in the application. We recommend the following:
  - Review your application code, middleware, and infrastructure configuration to ensure the Cache-Control headers set for authenticated paths prevent inappropriate caching
  - For application paths that require caching, do not allow user-specific or sensitive authenticated information to be included in the response data or headers

## References
- https://github.com/workos/authkit-nextjs/security/advisories/GHSA-p8pf-44ff-93gf
- https://nvd.nist.gov/vuln/detail/CVE-2025-64762
- https://github.com/workos/authkit-nextjs/commit/94cf438124993abb0e7c19dac64c3cb5724a15ea
- https://github.com/workos/authkit-nextjs
- https://github.com/workos/authkit-nextjs/releases/tag/v2.11.1
