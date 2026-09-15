# [M] Next.js: Unauthenticated disclosure of internal Server Function endpoints

## Summary
Severity: Medium
Advisory: GHSA-955p-x3mx-jcvp
CVE: CVE-2026-64643
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-955p-x3mx-jcvp
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <15.5.21
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
## Impact

In Next.js applications using App Router, Server Actions (`use server`) or `use cache` endpoints can be disclosed bypassing any authentication on the pages where these endpoints are usually used.

Server Action IDs can be disclosed to unauthenticated users via publicly served client artifacts (for example, static chunks containing action references).

Affected users are applications using App Router + Server Actions.  

By itself, this disclosure is typically a recon/enumeration primitive; however, it can increase risk when combined with other weaknesses.
 
## Workarounds

Never assume any authentication claims at the `use cache` or `use server` boundary. Always authenticate within the boundary.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-955p-x3mx-jcvp
- https://github.com/vercel/next.js/commit/1b0c3ae912a3ad925c60065cc8d55b070fa8bcd3
- https://github.com/vercel/next.js/commit/ff12a6124e1504f17b62de948b8a553fdecaef7b
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.21
- https://github.com/vercel/next.js/releases/tag/v16.2.11
