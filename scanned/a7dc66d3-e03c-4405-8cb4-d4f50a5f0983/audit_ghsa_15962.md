# [M] Denial of Service condition in Next.js image optimization

## Summary
Severity: Medium
Advisory: GHSA-g77x-44xx-532m
CVE: CVE-2024-47831
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-14
Source: https://github.com/advisories/GHSA-g77x-44xx-532m
Type: github-advisory

## Affected
- npm: `next` — affected >=10.0.0 <14.2.7

## Details
### Impact
The image optimization feature of Next.js contained a vulnerability which allowed for a potential Denial of Service (DoS) condition which could lead to excessive CPU consumption.

**Not affected:**
- The `next.config.js` file is configured with `images.unoptimized` set to `true` or `images.loader` set to a non-default value.
- The Next.js application is hosted on Vercel. 

### Patches
This issue was fully patched in Next.js `14.2.7`. We recommend that users upgrade to at least this version.

### Workarounds
Ensure that the `next.config.js` file has either `images.unoptimized`, `images.loader` or `images.loaderFile` assigned.

#### Credits
Brandon Dahler (brandondahler), AWS
Dimitrios Vlastaras

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-g77x-44xx-532m
- https://nvd.nist.gov/vuln/detail/CVE-2024-47831
- https://github.com/vercel/next.js/commit/d11cbc9ff0b1aaefabcba9afe1e562e0b1fde65a
- https://github.com/vercel/next.js
