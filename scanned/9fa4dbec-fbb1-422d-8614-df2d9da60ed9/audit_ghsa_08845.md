# [M] Next.js vulnerable to cache poisoning in React Server Component responses

## Summary
Severity: Medium
Advisory: GHSA-wfc6-r584-vfw7
CVE: CVE-2026-44576
CWE: CWE-436
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-wfc6-r584-vfw7
Type: github-advisory

## Affected
- npm: `next` — affected >=14.2.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
### Impact

Applications using React Server Components can be vulnerable to cache poisoning when shared caches do not correctly partition response variants. Under affected conditions, an attacker can cause an RSC response to be served from the original URL and poison shared cache entries so later visitors receive component payloads instead of the expected HTML.

### Fix

We now validate and interpret `RSC` request headers consistently across request classification and rendering, and we enforce the intended cache-busting behavior so RSC payloads are not unexpectedly served from the original URL.

### Workarounds

If you cannot upgrade immediately, ensure your CDN or reverse proxy keys on the relevant RSC request headers and honors `Vary`, or disable shared caching for affected App Router and RSC responses.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-wfc6-r584-vfw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44576
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.16
- https://github.com/vercel/next.js/releases/tag/v16.2.5
