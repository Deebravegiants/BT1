# [M] Next.js: Unbounded Server Action payload in Edge runtime

## Summary
Severity: Medium
Advisory: GHSA-4c39-4ccg-62r3
CVE: CVE-2026-64646
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-4c39-4ccg-62r3
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <15.5.21
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
## Impact

Requests targeting Next.js applications using App Router with at least one Server Action can lead to excessive memory consumption if that Server Actions uses the Edge runtime

## Workarounds

If you cannot upgrade, ensure your hosting provider limits the request's body size. 5 MiB should be allowed at max by your hosting provider.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-4c39-4ccg-62r3
- https://github.com/vercel/next.js/commit/57c31f724d746e86a9e8b92aa8be538a922446a4
- https://github.com/vercel/next.js/commit/9a4651e754f70b12e397694ffc41f44c3ba8cc17
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.21
- https://github.com/vercel/next.js/releases/tag/v16.2.11
