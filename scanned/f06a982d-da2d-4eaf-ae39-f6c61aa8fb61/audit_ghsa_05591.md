# [H] React Server Components have multiple Denial of Service Vulnerabilities

## Summary
Severity: High
Advisory: GHSA-83fc-fqcc-2hmg
CVE: CVE-2026-23864
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-83fc-fqcc-2hmg
Type: github-advisory

## Affected
- npm: `react-server-dom-parcel` — affected >=19.0.0 <19.0.4
- npm: `react-server-dom-turbopack` — affected >=19.1.0-canary-7130d0c6-20241212 <19.1.5
- npm: `react-server-dom-webpack` — affected >=19.2.0-canary-63779030-20250328 <19.2.4
- npm: `react-server-dom-turbopack` — affected >=19.0.0 <19.0.4
- npm: `react-server-dom-parcel` — affected >=19.1.0-canary-7130d0c6-20241212 <19.1.5
- npm: `react-server-dom-parcel` — affected >=19.2.0-canary-63779030-20250328 <19.2.4
- npm: `react-server-dom-webpack` — affected >=19.1.0-canary-7130d0c6-20241212 <19.1.5
- npm: `react-server-dom-webpack` — affected >=19.0.0 <19.0.4
- npm: `react-server-dom-turbopack` — affected >=19.2.0-canary-63779030-20250328 <19.2.4

## Details
## Impact

It was found that the fixes to address DoS in React Server Components were incomplete and we found multiple denial of service vulnerabilities still exist in React Server Components.

We recommend updating immediately.

The vulnerability exists in versions 19.0.0, 19.0.1, 19.0.2, 19.0.3, 19.1.0, 19.1.1, 19.1.2, 19.1.3, 19.1.4, 19.2.0, 19.2.1, 19.2.2, 19.2.3 of:

- [react-server-dom-webpack](https://www.npmjs.com/package/react-server-dom-webpack)  
- [react-server-dom-parcel](https://www.npmjs.com/package/react-server-dom-parcel)  
- [react-server-dom-turbopack](https://www.npmjs.com/package/react-server-dom-turbopack?activeTab=readme)

The vulnerabilities are triggered by sending specially crafted HTTP requests to Server Function endpoints, and could lead to server crashes, out-of-memory exceptions or excessive CPU usage; depending on the vulnerable code path being exercised, the application configuration and application code.

## Patches

Fixes were back ported to versions 19.0.4, 19.1.5, and 19.2.4.

If you are using any of the above packages please upgrade to any of the fixed versions immediately.

If your app’s React code does not use a server, your app is not affected by this vulnerability. If your app does not use a framework, bundler, or bundler plugin that supports React Server Components, your app is not affected by this vulnerability.

## References

See the [blog post](https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components) for more information and upgrade instructions.

## References
- https://github.com/facebook/react/security/advisories/GHSA-83fc-fqcc-2hmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-23864
- https://github.com/facebook/react
- https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components
- https://www.facebook.com/security/advisories/cve-2026-23864
