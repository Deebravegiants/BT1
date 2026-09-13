# [M] webpack-dev-server vulnerable to denial of service via a malformed Host or Origin header

## Summary
Severity: Medium
Advisory: GHSA-m28w-2pqf-7qgj
CVE: CVE-2026-14631
CWE: CWE-20, CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-m28w-2pqf-7qgj
Type: github-advisory

## Affected
- npm: `webpack-dev-server` — affected >=0 <5.2.6

## Details
### Impact

An unauthenticated peer that can reach the `webpack-dev-server` process can terminate it by sending either a normal HTTP request with a malformed `Host` header, or a WebSocket upgrade to the default `/ws` endpoint with a malformed `Origin` header. The malformed header triggers an uncaught exception in the host-validation path and crashes the dev server process.

### Patches

Fixed in `webpack-dev-server` 5.2.6 by treating malformed `Host` and `Origin` header values as invalid rather than throwing (see [PR #5699](https://github.com/webpack/webpack-dev-server/pull/5699)).

### Workarounds

Keep the dev server bound to `localhost` (the default) and do not expose it to untrusted networks.

## References
- https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-m28w-2pqf-7qgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-14631
- https://github.com/webpack/webpack-dev-server/pull/5699
- https://github.com/webpack/webpack-dev-server/commit/f21ed0f44aceb6132abb591ee8b60d770b6e489f
- https://cna.openjsf.org/security-advisories.html
- https://github.com/webpack/webpack-dev-server
