# [M] Next.js: Denial of Service in the Image Optimization API using SVGs

## Summary
Severity: Medium
Advisory: GHSA-q8wf-6r8g-63ch
CVE: CVE-2026-64644
CWE: CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-q8wf-6r8g-63ch
Type: github-advisory

## Affected
- npm: `next` — affected >=15.5.0 <15.5.21
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
### Impact

When self-hosting Next.js with the default image loader, the Image Optimization API can optimize remotely hosted images if configured (not enabled by default). If those images contain malicious content, they can cause CPU exhaustion in  `/_next/image` endpoints.

- If you are using `config.images.remotePatterns`, only the patterns in that array are impacted.
- If you are using `config.images.unoptimized: true`, you are NOT impacted.
- If you are using `config.images.loader: 'custom'`, you are NOT impacted.
- If you are using Vercel, you are NOT impacted.

### Workarounds

If you cannot upgrade immediately, you can avoid the expensive work by setting `config.experimental.imgOptSkipMetadata : true`.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-q8wf-6r8g-63ch
- https://github.com/vercel/next.js/pull/96006
- https://github.com/vercel/next.js/commit/93cb90891402fa4c47798d03cb9e05c13233766c
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.21
- https://github.com/vercel/next.js/releases/tag/v16.2.11
