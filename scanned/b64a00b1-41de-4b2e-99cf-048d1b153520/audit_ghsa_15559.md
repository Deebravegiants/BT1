# [H] Next.js Cache Poisoning

## Summary
Severity: High
Advisory: GHSA-gp8f-8m3g-qvj9
CVE: CVE-2024-46982
CWE: CWE-349, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-gp8f-8m3g-qvj9
Type: github-advisory

## Affected
- npm: `next` — affected >=13.5.1 <13.5.7
- npm: `next` — affected >=14.0.0 <14.2.10

## Details
### Impact

By sending a crafted HTTP request, it is possible to poison the cache of a non-dynamic server-side rendered route in the pages router (this does not affect the app router). When this crafted request is sent it could coerce Next.js to cache a route that is meant to not be cached and send a `Cache-Control: s-maxage=1, stale-while-revalidate` header which some upstream CDNs may cache as well. 

To be potentially affected all of the following must apply: 

- Next.js between 13.5.1 and 14.2.9
- Using pages router
- Using non-dynamic server-side rendered routes e.g. `pages/dashboard.tsx` not `pages/blog/[slug].tsx`

The below configurations are unaffected:

- Deployments using only app router
- Deployments on [Vercel](https://vercel.com/) are not affected


### Patches

This vulnerability was resolved in Next.js v13.5.7, v14.2.10, and later. We recommend upgrading regardless of whether you can reproduce the issue or not.

### Workarounds

There are no official or recommended workarounds for this issue, we recommend that users patch to a safe version.

#### Credits

- Allam Rachid (zhero_)
- Henry Chen

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-gp8f-8m3g-qvj9
- https://nvd.nist.gov/vuln/detail/CVE-2024-46982
- https://github.com/vercel/next.js/commit/7ed7f125e07ef0517a331009ed7e32691ba403d3
- https://github.com/vercel/next.js/commit/bd164d53af259c05f1ab434004bcfdd3837d7cda
- https://github.com/vercel/next.js
