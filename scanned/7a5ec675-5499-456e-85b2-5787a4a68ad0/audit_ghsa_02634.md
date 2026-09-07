# [H] XSS in Image Optimization API for Next.js

## Summary
Severity: High
Advisory: GHSA-9gr3-7897-pp7m
CVE: CVE-2021-39178
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-9gr3-7897-pp7m
Type: github-advisory

## Affected
- npm: `next` — affected >=10.0.0 <11.1.1

## Details
### Impact
- **Affected:** All of the following must be true to be affected
    - Next.js between version 10.0.0 and 11.1.0
    - The `next.config.js` file has [`images.domains`](https://nextjs.org/docs/basic-features/image-optimization#domains) array assigned
    - The image host assigned in [`images.domains`](https://nextjs.org/docs/basic-features/image-optimization#domains) allows user-provided SVG
- **Not affected**: The `next.config.js` file has [`images.loader`](https://nextjs.org/docs/basic-features/image-optimization#loader) assigned to something other than default
- **Not affected**: Deployments on [Vercel](https://vercel.com) are not affected

### Patches
[Next.js v11.1.1](https://github.com/vercel/next.js/releases/tag/v11.1.1)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-9gr3-7897-pp7m
- https://nvd.nist.gov/vuln/detail/CVE-2021-39178
- https://github.com/vercel/next.js/pull/28620
- https://github.com/vercel/next.js/commit/7afc97c5744b38bdf36aa7f87625f438224688aa
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v11.1.1
