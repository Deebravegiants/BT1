# [M] webpack-dev-server vulnerable to HMR WebSocket interception via permissive user proxies

## Summary
Severity: Medium
Advisory: GHSA-mx8g-39q3-5c79
CVE: CVE-2026-9595
CWE: CWE-346, CWE-441
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-mx8g-39q3-5c79
Type: github-advisory

## Affected
- npm: `webpack-dev-server` — affected >=0 <5.2.5

## Details
### Impact

When a user-configured proxy on `webpack-dev-server` has a broad context (e.g. `/`) and `ws: true`, it also intercepts the dev server's own HMR WebSocket and forwards it to the proxy target. This leaks the browser's cookies and `Origin` header to the backend, bypasses the dev server's Host/Origin validation, and corrupts the HMR socket (both HMR and the proxy end up writing to the same socket).

### Patches

Fixed in `webpack-dev-server` 5.2.5.

### Workarounds

Scope user-defined proxy `context` to specific paths instead of `/`, or omit `ws: true` from the proxy entry when WebSocket forwarding is not required.

## References
- https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-mx8g-39q3-5c79
- https://nvd.nist.gov/vuln/detail/CVE-2026-9595
- https://github.com/facebook/create-react-app/pull/7444
- https://github.com/webpack/webpack-dev-server/pull/4316
- https://github.com/vuejs/vue-cli/commit/72ba7505aff2a8314e82aa5082379a77504a1fcb
- https://cna.openjsf.org/security-advisories.html
- https://github.com/webpack/webpack-dev-server
