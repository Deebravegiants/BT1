# [C] React Server Components are Vulnerable to RCE

## Summary
Severity: Critical
Advisory: GHSA-fv66-9v8q-g76r
CVE: CVE-2025-55182
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-fv66-9v8q-g76r
Type: github-advisory

## Affected
- npm: `react-server-dom-webpack` — affected >=19.0.0 <19.0.1
- npm: `react-server-dom-webpack` — affected >=19.1.0 <19.1.2
- npm: `react-server-dom-webpack` — affected >=19.2.0 <19.2.1
- npm: `react-server-dom-turbopack` — affected >=19.0.0 <19.0.1
- npm: `react-server-dom-turbopack` — affected >=19.1.0 <19.1.2
- npm: `react-server-dom-turbopack` — affected >=19.2.0 <19.2.1
- npm: `react-server-dom-parcel` — affected >=19.0.0 <19.0.1
- npm: `react-server-dom-parcel` — affected >=19.1.0 <19.1.2
- npm: `react-server-dom-parcel` — affected >=19.2.0 <19.2.1

## Details
### Impact

There is an unauthenticated remote code execution vulnerability in React Server Components.

We recommend upgrading immediately.

The vulnerability is present in versions 19.0.0, 19.1.0, 19.1.1, and 19.2.0 of:
* [react-server-dom-webpack](https://www.npmjs.com/package/react-server-dom-webpack)
* [react-server-dom-parcel](https://www.npmjs.com/package/react-server-dom-parcel)
* [react-server-dom-turbopack](https://www.npmjs.com/package/react-server-dom-turbopack?activeTab=readme)

### Patches

A fix was introduced in versions [19.0.1](https://github.com/facebook/react/releases/tag/v19.0.1), [19.1.2](https://github.com/facebook/react/releases/tag/v19.1.2), and [19.2.1](https://github.com/facebook/react/releases/tag/v19.2.1). If you are using any of the above packages please upgrade to any of the fixed versions immediately.

If your app’s React code does not use a server, your app is not affected by this vulnerability. If your app does not use a framework, bundler, or bundler plugin that supports React Server Components, your app is not affected by this vulnerability.

### References

See the [blog post](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components) for more information and upgrade instructions.

## References
- https://github.com/facebook/react/security/advisories/GHSA-fv66-9v8q-g76r
- https://nvd.nist.gov/vuln/detail/CVE-2025-55182
- https://github.com/facebook/react/pull/35277
- https://github.com/facebook/react/commit/7dc903cd29dac55efb4424853fd0442fef3a8700
- https://github.com/ejpir/CVE-2025-55182-poc
- https://github.com/facebook/react
- https://github.com/facebook/react/releases/tag/v19.0.1
- https://github.com/facebook/react/releases/tag/v19.1.2
- https://github.com/facebook/react/releases/tag/v19.2.1
- https://news.ycombinator.com/item?id=46136026
- https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
- https://www.facebook.com/security/advisories/cve-2025-55182
- http://www.openwall.com/lists/oss-security/2025/12/03/4
