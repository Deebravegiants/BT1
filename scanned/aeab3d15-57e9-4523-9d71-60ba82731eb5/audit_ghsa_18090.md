# [M] Next.js Content Injection Vulnerability for Image Optimization

## Summary
Severity: Medium
Advisory: GHSA-xv57-4mr9-wg8v
CVE: CVE-2025-55173
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-xv57-4mr9-wg8v
Type: github-advisory

## Affected
- npm: `next` — affected >=0.9.9 <14.2.31
- npm: `next` — affected >=15.0.0 <15.4.5

## Details
A vulnerability in **Next.js Image Optimization** has been fixed in **v15.4.5** and **v14.2.31**. The issue allowed attacker-controlled external image sources to trigger file downloads with arbitrary content and filenames under specific configurations. This behavior could be abused for phishing or malicious file delivery.

All users relying on `images.domains` or `images.remotePatterns` are encouraged to upgrade and verify that external image sources are strictly validated.

More details at [Vercel Changelog](https://vercel.com/changelog/cve-2025-55173)

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-xv57-4mr9-wg8v
- https://nvd.nist.gov/vuln/detail/CVE-2025-55173
- https://github.com/vercel/next.js/commit/6b12c60c61ee80cb0443ccd20de82ca9b4422ddd
- https://github.com/vercel/next.js
- https://vercel.com/changelog/cve-2025-55173
- http://vercel.com/changelog/cve-2025-55173
