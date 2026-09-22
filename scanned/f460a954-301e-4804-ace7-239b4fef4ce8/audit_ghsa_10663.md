# [M] @hono/node-server: Middleware bypass via repeated slashes in serveStatic

## Summary
Severity: Medium
Advisory: GHSA-92pp-h63x-v22m
CVE: CVE-2026-39406
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-92pp-h63x-v22m
Type: github-advisory

## Affected
- npm: `@hono/node-server` — affected >=0 <1.19.13

## Details
## Summary

A path handling inconsistency in `serveStatic` allows protected static files to be accessed by using repeated slashes (`//`) in the request path.

When route-based middleware (e.g., `/admin/*`) is used for authorization, the router may not match paths containing repeated slashes, while `serveStatic` resolves them as normalized paths. This can lead to a middleware bypass.

## Details

The routing layer and `serveStatic` handle repeated slashes differently.

For example:

- `/admin/secret.txt` => matches `/admin/*`
- `//admin/secret.txt` => may not match `/admin/*`

This inconsistency allows a request such as:

```
GET //admin/secret.txt
```

to bypass middleware registered on `/admin/*` and access protected files.

## Impact

An attacker can access static files that are intended to be protected by route-based middleware by using repeated slashes in the request path.

This can lead to unauthorized access to sensitive files under the static root.

This issue affects applications that rely on `serveStatic` together with route-based middleware for access control.

## References
- https://github.com/honojs/node-server/security/advisories/GHSA-92pp-h63x-v22m
- https://nvd.nist.gov/vuln/detail/CVE-2026-39406
- https://github.com/honojs/node-server/commit/025c30f55d589ddbe6048b151d77e904f67a8cc2
- https://github.com/honojs/node-server
- https://github.com/honojs/node-server/releases/tag/v1.19.13
