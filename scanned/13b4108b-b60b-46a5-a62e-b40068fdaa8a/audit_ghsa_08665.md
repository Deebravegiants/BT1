# [H] Facebook React has a Denial of Service Vulnerability in React Server Components

## Summary
Severity: High
Advisory: GHSA-rv78-f8rc-xrxh
CVE: CVE-2026-23870
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-rv78-f8rc-xrxh
Type: github-advisory

## Affected
- npm: `react-server-dom-parcel` — affected >=19.0.0 <19.0.6
- npm: `react-server-dom-turbopack` — affected >=19.0.0 <19.0.6
- npm: `react-server-dom-webpack` — affected >=19.0.0 <19.0.6
- npm: `react-server-dom-parcel` — affected >=19.1.0 <19.1.7
- npm: `react-server-dom-turbopack` — affected >=19.1.0 <19.1.7
- npm: `react-server-dom-webpack` — affected >=19.1.0 <19.1.7
- npm: `react-server-dom-parcel` — affected >=19.2.0 <19.2.6
- npm: `react-server-dom-turbopack` — affected >=19.2.0 <19.2.6
- npm: `react-server-dom-webpack` — affected >=19.2.0 <19.2.6

## Details
## Impact

A denial of service vulnerability could be triggered by sending specially crafted HTTP requests to server function endpoints, this could lead to out-of-memory exceptions or excessive CPU usage.

We recommend updating immediately.

The vulnerability exists in versions 19.0.0 through 19.0.5, 19.1.0 through 19.1.6, and 19.2.0 through 19.2.5 of:

[react-server-dom-webpack](https://www.npmjs.com/package/react-server-dom-webpack)
[react-server-dom-parcel](https://www.npmjs.com/package/react-server-dom-parcel)
[react-server-dom-turbopack](https://www.npmjs.com/package/react-server-dom-turbopack?activeTab=readme)

## Patches

Fixes were back ported to versions 19.0.6, 19.1.7, and 19.2.6.

If you are using any of the above packages please upgrade to any of the fixed versions immediately.

If your app’s React code does not use a server, your app is not affected by this vulnerability. If your app does not use a framework, bundler, or bundler plugin that supports React Server Components, your app is not affected by this vulnerability.

References
See the [blog post](https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components) for more information and upgrade instructions.

## References
- https://github.com/facebook/react/security/advisories/GHSA-rv78-f8rc-xrxh
- https://github.com/vercel/next.js/security/advisories/GHSA-8h8q-6873-q5fj
- https://github.com/vitejs/vite-plugin-react/security/advisories/GHSA-w94c-4vhp-22gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-23870
- https://github.com/facebook/react
