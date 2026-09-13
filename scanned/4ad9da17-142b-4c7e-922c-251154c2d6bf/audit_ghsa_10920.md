# [H] @hono/node-server has authorization bypass for protected static paths via encoded slashes in Serve Static Middleware

## Summary
Severity: High
Advisory: GHSA-wc8c-qw6v-h7f6
CVE: CVE-2026-29087
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-wc8c-qw6v-h7f6
Type: github-advisory

## Affected
- npm: `@hono/node-server` — affected >=0 <1.19.10

## Details
## Summary

When using @hono/node-server's static file serving together with route-based middleware protections (e.g. protecting `/admin/*`), inconsistent URL decoding can allow protected static resources to be accessed without authorization.

In particular, paths containing encoded slashes (`%2F`) may be evaluated differently by routing/middleware matching versus static file path resolution, enabling a bypass where middleware does not run but the static file is still served.

## Details

The routing layer and the node-server static handler normalize request paths differently. The router preserves `%2F` as a literal string when matching routes, while the static handler decodes `%2F` into `/` before resolving the filesystem path.

Example request:

- `/admin%2Fsecret.html`

This may:
- fail to match middleware intended for `/admin/*`, but
- still be resolved by the static handler as `/admin/secret.html` under the configured static root.

This does not allow access outside the configured static root and is not a path traversal vulnerability.

## Impact

An unauthenticated attacker could bypass route-based authorization protections for protected static resources by supplying paths containing encoded slashes.

Applications relying solely on route-based middleware to protect static subpaths under the same static root may have exposed those resources.

## References
- https://github.com/honojs/node-server/security/advisories/GHSA-wc8c-qw6v-h7f6
- https://nvd.nist.gov/vuln/detail/CVE-2026-29087
- https://github.com/honojs/node-server/commit/455015be1697dd89974a68b70350ea7b2d126d2e
- https://github.com/honojs/node-server
