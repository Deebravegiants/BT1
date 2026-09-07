# [H] @asymmetric-effort/specifyjs: URL parse failure silently allows request

## Summary
Severity: High
Advisory: GHSA-8882-frvv-92w4
CVE: CVE-2026-50288
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-8882-frvv-92w4
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/specifyjs` — affected >=0 <0.2.136

## Details
## Finding

**Location**: `core/src/shared/secure-fetch.ts:42-45`

When `new URL()` throws a parse error, the `assertSecureUrl` function returned without throwing, silently allowing the request to proceed without HTTPS validation.

## Status

**Fixed in v0.2.136** — The catch block now throws an error instead of silently returning.

## References
- https://github.com/asymmetric-effort/specifyjs/security/advisories/GHSA-8882-frvv-92w4
- https://github.com/asymmetric-effort/specifyjs/commit/25d1fb491d99479efdf501f5f75e0bb80c908f0a
- https://github.com/asymmetric-effort/specifyjs
- https://github.com/asymmetric-effort/specifyjs/releases/tag/v0.2.136
