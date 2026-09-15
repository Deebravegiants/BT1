# [M] Next.js: Cache confusion of response bodies for requests with bodies

## Summary
Severity: Medium
Advisory: GHSA-68g3-v927-f742
CVE: CVE-2026-64648
CWE: CWE-524
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-68g3-v927-f742
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <15.5.21
- npm: `next` — affected >=16.0.0 <16.2.11

## Details
## Impact

A server-side `fetch` with a request body may return a cached **response** body from a different request to the same URL but different body. Confidential data in the `POST`'s **response** body would then leak to unauthorized requests. Though the request itself will not be deduped.

This only applies to `fetch` calls with a request that has a different init than the one passed to `fetch`.
Safe: `fetch(new Request(init), init)`
Unsafe: `fetch(new Request(init), aDifferentInit)`

## Workarounds

No workaround exists besides upgrading. Applications using Pages Router are not vulnerable.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-68g3-v927-f742
- https://github.com/vercel/next.js/commit/062f66700b52a5d6bba2c0605d55577ab7ad262c
- https://github.com/vercel/next.js/commit/73b94872bc343d09494b50394d8c08eb9fc8e56a
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v15.5.21
- https://github.com/vercel/next.js/releases/tag/v16.2.11
