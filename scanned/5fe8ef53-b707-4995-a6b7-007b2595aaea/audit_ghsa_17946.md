# [M] Next.js Affected by Cache Key Confusion for Image Optimization API Routes

## Summary
Severity: Medium
Advisory: GHSA-g5qg-72qw-gw5v
CVE: CVE-2025-57752
CWE: CWE-524
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-g5qg-72qw-gw5v
Type: github-advisory

## Affected
- npm: `next` — affected >=0.9.9 <14.2.31
- npm: `next` — affected >=15.0.0 <15.4.5

## Details
A vulnerability in Next.js Image Optimization has been fixed in v15.4.5 and v14.2.31. When images returned from API routes vary based on request headers (such as `Cookie` or `Authorization`), these responses could be incorrectly cached and served to unauthorized users due to a cache key confusion bug.

All users are encouraged to upgrade if they use API routes to serve images that depend on request headers and have image optimization enabled.

More details at [Vercel Changelog](https://vercel.com/changelog/cve-2025-57752)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-g5qg-72qw-gw5v
- https://nvd.nist.gov/vuln/detail/CVE-2025-57752
- https://github.com/vercel/next.js/pull/82114
- https://github.com/vercel/next.js/commit/6b12c60c61ee80cb0443ccd20de82ca9b4422ddd
- https://github.com/vercel/next.js
- https://vercel.com/changelog/cve-2025-57752
