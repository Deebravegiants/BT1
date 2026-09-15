# [H] Hono vulnerable to arbitrary file access via serveStatic vulnerability 

## Summary
Severity: High
Advisory: GHSA-q5qw-h33p-qvwr
CVE: CVE-2026-29045
CWE: CWE-177
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-q5qw-h33p-qvwr
Type: github-advisory

## Affected
- npm: `hono` — affected >=0 <4.12.4

## Details
## Summary

When using `serveStatic` together with route-based middleware protections (e.g. `app.use('/admin/*', ...)`), inconsistent URL decoding allowed protected static resources to be accessed without authorization.

The router used `decodeURI`, while `serveStatic` used `decodeURIComponent`. This mismatch allowed paths containing encoded slashes (`%2F`) to bypass middleware protections while still resolving to the intended filesystem path.


## Details

The routing layer preserved `%2F` as a literal string, while `serveStatic` decoded it into `/` before resolving the file path.

Example:

Request: `/admin%2Fsecret.html`

- Router sees: `/admin%2Fsecret.html` → does not match `/admin/*`
- Static handler resolves: `/admin/secret.html`

As a result, static files under the configured static root could be served without triggering route-based protections.

This only affects applications that both:

- Protect subpaths using route-based middleware, and
- Serve files from the same static root using `serveStatic`.

This does **not** allow access outside the static root and is **not** a path traversal vulnerability.


## Impact

An unauthenticated attacker could bypass route-based authorization for protected static resources by supplying paths containing encoded slashes.

Applications relying solely on route-based middleware to protect static subpaths may have exposed those resources.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-q5qw-h33p-qvwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-29045
- https://github.com/honojs/hono/commit/6a0607a929d888893f0c91d92dce2fcfdb3662a3
- https://github.com/honojs/hono
