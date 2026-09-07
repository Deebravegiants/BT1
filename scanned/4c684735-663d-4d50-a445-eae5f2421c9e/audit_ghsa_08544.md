# [H] Next.js Vulnerable to Denial of Service with Server Components

## Summary
Severity: High
Advisory: GHSA-8h8q-6873-q5fj
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-8h8q-6873-q5fj
Type: github-advisory

## Affected
- npm: `next` — affected >=13.0.0 <15.5.16
- npm: `next` — affected >=16.0.0 <16.2.5

## Details
A vulnerability affects certain React Server Components packages for versions 19.x and frameworks that use the affected packages, including Next.js 13.x, 14.x, 15.x, and 16.x using the App Router. The issue is tracked upstream as [CVE-2026-23870](https://github.com/facebook/react/security/advisories/GHSA-rv78-f8rc-xrxh). 

A specially crafted HTTP request can be sent to any App Router Server Function endpoint that, when deserialized, may trigger excessive CPU usage. This can result in denial of service in unpatched environments.

## References
- https://github.com/facebook/react/security/advisories/GHSA-rv78-f8rc-xrxh
- https://github.com/vercel/next.js/security/advisories/GHSA-8h8q-6873-q5fj
- https://github.com/vitejs/vite-plugin-react/security/advisories/GHSA-w94c-4vhp-22gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-23870
- https://github.com/vercel/next.js
