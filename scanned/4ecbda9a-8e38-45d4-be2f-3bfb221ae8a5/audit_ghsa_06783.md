# [M] @asymmetric-effort/specifyjs: No redirect target validation in secureFetch

## Summary
Severity: Medium
Advisory: GHSA-j5qp-p44g-2m49
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-j5qp-p44g-2m49
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/specifyjs` — affected >=0 <0.2.136

## Details
## Finding

**Location**: `core/src/shared/secure-fetch.ts`

`assertSecureUrl` validated only the initial request URL. The `fetch()` API follows redirects by default (up to 20 hops). A request to a valid `https://` URL could redirect to `http://internal-service/` or other unvalidated destinations.

## Status

**Fixed in v0.2.136** — `secureFetch` now defaults to `redirect: 'error'` which rejects any redirect. Callers can override with `{ redirect: 'follow' }` if they trust the target.

## References
- https://github.com/asymmetric-effort/specifyjs/security/advisories/GHSA-j5qp-p44g-2m49
- https://github.com/asymmetric-effort/specifyjs/commit/25d1fb491d99479efdf501f5f75e0bb80c908f0a
- https://github.com/asymmetric-effort/specifyjs
