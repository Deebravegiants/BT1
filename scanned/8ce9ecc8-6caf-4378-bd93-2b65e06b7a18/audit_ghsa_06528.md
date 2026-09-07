# [H] Next.js: Middleware / Proxy bypass in App Router applications using Turbopack and single locale

## Summary
Severity: High
Advisory: GHSA-6gpp-xcg3-4w24
CVE: CVE-2026-64642
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-6gpp-xcg3-4w24
Type: github-advisory

## Affected
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
## Impact

Crafted requests targeting Next.js applications using App Router built with Turbopack and a **single** entry in `config.i18n.locales` can bypass middleware/proxy based authentication.

## Workarounds

If you cannot upgrade immediately, enforce authorization in the page's server-side data path instead of relying solely on middleware.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-6gpp-xcg3-4w24
- https://github.com/vercel/next.js/pull/96014
- https://github.com/vercel/next.js/commit/6bf4df14508ad6c0cd46af50c6051ee42f2d9151
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v16.2.11
