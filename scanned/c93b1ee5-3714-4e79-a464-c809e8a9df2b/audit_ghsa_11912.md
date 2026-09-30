# [M] Next.js: Unbounded next/image disk cache growth can exhaust storage

## Summary
Severity: Medium
Advisory: GHSA-3x4c-7xq6-9pq8
CVE: CVE-2026-27980
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-3x4c-7xq6-9pq8
Type: github-advisory

## Affected
- npm: `next` — affected >=16.0.0-beta.0 <16.1.7
- npm: `next` — affected >=10.0.0 <15.5.14

## Details
## Summary
The default Next.js image optimization disk cache (`/_next/image`) did not have a configurable upper bound, allowing unbounded cache growth.

## Impact
An attacker could generate many unique image-optimization variants and exhaust disk space, causing denial of service. Note that this does not impact platforms that have their own image optimization capabilities, such as Vercel.

## Patches
Fixed by adding an LRU-backed disk cache with `images.maximumDiskCacheSize`, including eviction of least-recently-used entries when the limit is exceeded. Setting `maximumDiskCacheSize: 0` disables disk caching. 

## Workarounds
If upgrade is not immediately possible:
- Periodically clean `.next/cache/images`.
- Reduce variant cardinality (e.g., tighten values for `images.localPatterns`, `images.remotePatterns`, and `images.qualities`)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-3x4c-7xq6-9pq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-27980
- https://github.com/vercel/next.js/commit/39eb8e0ac498b48855a0430fbf4c22276a73b4bd
- https://github.com/vercel/next.js
- https://github.com/vercel/next.js/releases/tag/v16.1.7
