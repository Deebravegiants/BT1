# [H] react-server-dom: Denial of Service in Server Functions

## Summary
Severity: High
Advisory: GHSA-wx67-qw84-cm4g
CVE: CVE-2026-44907
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-wx67-qw84-cm4g
Type: github-advisory

## Affected
- npm: `react-server-dom-webpack` — affected >=19.0.0 <19.0.8
- npm: `react-server-dom-turbopack` — affected >=19.0.0 <19.0.8
- npm: `react-server-dom-turbopack` — affected >=19.1.0 <19.1.9
- npm: `react-server-dom-parcel` — affected >=19.1.0 <19.1.9
- npm: `react-server-dom-webpack` — affected >=19.1.0 <19.1.9
- npm: `react-server-dom-turbopack` — affected >=19.2.0 <19.2.8
- npm: `react-server-dom-parcel` — affected >=19.2.0 <19.2.8
- npm: `react-server-dom-webpack` — affected >=19.2.0 <19.2.8

## Details
### Impact

A denial of service vulnerability could be triggered by sending specially crafted HTTP requests to server function endpoints, this could lead to out-of-memory exceptions or excessive CPU usage.

We recommend updating immediately.

The vulnerability exists in versions 19.0.0 through 19.0.7, 19.1.0 through 19.1.8, and 19.2.0 through 19.2.7 of:
- react-server-dom-webpack
- react-server-dom-parcel
- react-server-dom-turbopack

### Patches

Fixes were back ported to versions 19.0.8, 19.1.9, and 19.2.8.

If you are using any of the above packages please upgrade to any of the fixed versions immediately.

If your app’s React code does not use a server, your app is not affected by this vulnerability. If your app does not use a framework, bundler, or bundler plugin that supports React Server Components, your app is not affected by this vulnerability.

## References
- https://github.com/react/react/security/advisories/GHSA-wx67-qw84-cm4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-44907
- https://github.com/react/react
