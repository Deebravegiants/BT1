# [M] Next Server Actions Source Code Exposure 

## Summary
Severity: Medium
Advisory: GHSA-w37m-7fhw-fmv9
CWE: CWE-1395, CWE-497, CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-12-11
Source: https://github.com/advisories/GHSA-w37m-7fhw-fmv9
Type: github-advisory

## Affected
- npm: `next` — affected >=15.0.0-canary.0 <15.0.6
- npm: `next` — affected >=15.1.1-canary.0 <15.1.10
- npm: `next` — affected >=15.2.0-canary.0 <15.2.7
- npm: `next` — affected >=15.3.0-canary.0 <15.3.7
- npm: `next` — affected >=15.4.0-canary.0 <15.4.9
- npm: `next` — affected >=15.5.1-canary.0 <15.5.8
- npm: `next` — affected >=15.6.0-canary.0 <15.6.0-canary.59
- npm: `next` — affected >=16.0.0-beta.0 <16.0.9
- npm: `next` — affected >=16.1.0-canary.0 <16.1.0-canary.17

## Details
A vulnerability affects certain React packages for versions 19.0.0, 19.0.1, 19.1.0, 19.1.1, 19.1.2, 19.2.0, and 19.2.1 and frameworks that use the affected packages, including Next.js 15.x and 16.x using the App Router. The issue is tracked upstream as [CVE-2025-55183](https://www.cve.org/CVERecord?id=CVE-2025-55183).

A malicious HTTP request can be crafted and sent to any App Router endpoint that can return the compiled source code of [Server Functions](https://react.dev/reference/rsc/server-functions). This could reveal business logic, but would not expose secrets unless they were hardcoded directly into [Server Function](https://react.dev/reference/rsc/server-functions) code.

## References
- https://github.com/vercel/next.js/security/advisories/GHSA-w37m-7fhw-fmv9
- https://github.com/vercel/next.js
- https://nextjs.org/blog/security-update-2025-12-11
- https://www.cve.org/CVERecord?id=CVE-2025-55183
