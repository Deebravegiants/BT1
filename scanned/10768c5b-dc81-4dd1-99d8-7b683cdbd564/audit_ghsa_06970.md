# [M] @asymmetric-effort/specifyjs: Localhost bypass incomplete (IPv6, 0.0.0.0, 127.x range)

## Summary
Severity: Medium
Advisory: GHSA-xw57-23p8-9wc5
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-xw57-23p8-9wc5
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/specifyjs` — affected >=0 <0.2.136

## Details
## Finding

**Location**: `core/src/shared/secure-fetch.ts:52-54`

The localhost exception allowed `localhost` and `127.0.0.1` but did not cover `0.0.0.0`, `[::1]` (IPv6 localhost), or the full `127.0.0.0/8` loopback range.

## Status

**Fixed in v0.2.136** — Localhost detection now covers `localhost`, `127.0.0.1`, `[::1]`, `0.0.0.0`, and the full `127.x.x.x` range.

## References
- https://github.com/asymmetric-effort/specifyjs/security/advisories/GHSA-xw57-23p8-9wc5
- https://github.com/asymmetric-effort/specifyjs/commit/25d1fb491d99479efdf501f5f75e0bb80c908f0a
- https://github.com/asymmetric-effort/specifyjs/commit/293124c51bf797c0f5cdae32981110545850a893
- https://github.com/asymmetric-effort/specifyjs
