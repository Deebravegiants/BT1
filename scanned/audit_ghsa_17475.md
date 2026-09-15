# [C] Next.js is vulnerable to RCE in React flight protocol

## Summary
Severity: Critical
Advisory: GHSA-9qr9-h5gf-34mp
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-9qr9-h5gf-34mp
Type: github-advisory

## Affected
- npm: `next` — affected >=14.3.0-canary.77 <15.0.5
- npm: `next` — affected >=15.1.0-canary.0 <15.1.9
- npm: `next` — affected >=15.2.0-canary.0 <15.2.6
- npm: `next` — affected >=15.3.0-canary.0 <15.3.6
- npm: `next` — affected >=15.4.0-canary.0 <15.4.8
- npm: `next` — affected >=15.5.0-canary.0 <15.5.7
- npm: `next` — affected >=16.0.0-canary.0 <16.0.7

## Details
A vulnerability affects certain React packages<sup>1</sup> for versions 19.0.0, 19.1.0, 19.1.1, and 19.2.0 and frameworks that use the affected packages, including Next.js 15.x and 16.x using the App Router. The issue is tracked upstream as [CVE-2025-55182](https://www.cve.org/CVERecord?id=CVE-2025-55182). 

Fixed in:
React: 19.0.1, 19.1.2, 19.2.1
Next.js: 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, 16.0.7, 15.6.0-canary.58, 16.1.0-canary.12+

The vulnerability also affects experimental canary releases starting with 14.3.0-canary.77. Users on any of the 14.3 canary builds should either downgrade to a 14.x stable release or 14.3.0-canary.76.

All users of stable 15.x or 16.x Next.js versions should upgrade to a patched, stable version immediately.

<sup>1</sup> The affected React packages are:
- react-server-dom-parcel
- react-server-dom-turbopack
- react-server-dom-webpack

## References
- https://github.com/facebook/react/security/advisories/GHSA-fv66-9v8q-g76r
- https://github.com/vercel/next.js/security/advisories/GHSA-9qr9-h5gf-34mp
- https://github.com/vitejs/vite-plugin-react/security/advisories/GHSA-fmh4-wr37-44fp
- https://nvd.nist.gov/vuln/detail/CVE-2025-55182
- https://github.com/vercel/next.js
