# [H] @fastify/static vulnerable to route guard bypass via path traversal

## Summary
Severity: High
Advisory: GHSA-83w8-p2f5-377r
CVE: CVE-2026-15074
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-83w8-p2f5-377r
Type: github-advisory

## Affected
- npm: `@fastify/static` — affected >=0 <10.1.1

## Details
### Impact

`@fastify/static` is vulnerable to a bypass of route-based middleware and guards via non-leading `..` and `%2E%2E` path segments. `find-my-way` does not normalize `..` when matching routes, so a request such as `/foo/../deep/secret.txt` matches the static plugin's catch-all instead of the guarded `/deep/*`. The `getPathnameForSend` helper introduced by the fix for [GHSA-x428-ghpx-8j92](https://github.com/fastify/fastify-static/security/advisories/GHSA-x428-ghpx-8j92) only guards against the `%2F` variant; `..` and `%2E%2E` survive the `decodeURI` + `encodeURI` round-trip and are then collapsed away by `@fastify/send`'s `path.normalize` before its own traversal guard runs.

Applications that rely on route-based middleware or guards to protect files served by `@fastify/static` can be bypassed with non-leading dot-dot path segments.

### Patches

Upgrade to `@fastify/static` 10.1.1.

### Workarounds

Do not use route-based middlewares or guards to protect files served by `@fastify/static`.

## References
- https://github.com/fastify/fastify-static/security/advisories/GHSA-83w8-p2f5-377r
- https://nvd.nist.gov/vuln/detail/CVE-2026-15074
- https://github.com/fastify/fastify-static/commit/db4276f846ba56b21f93768cd6636ee5e2fc58b1
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify-static
- https://github.com/fastify/fastify-static/releases/tag/v10.1.1
