# [M] @asymmetric-effort/specifyjs: `data:` URI allowed without size restriction

## Summary
Severity: Medium
Advisory: GHSA-2944-57xv-2682
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-2944-57xv-2682
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/specifyjs` — affected >=0 <0.2.136

## Details
## Finding

**Location**: `core/src/shared/secure-fetch.ts:33-35`

`data:` URIs were allowed without any restriction. While `data:` URIs don't make network requests, they can be used for memory exhaustion via very large data URIs.

## Status

**Fixed in v0.2.136** — `data:` URIs are now limited to 1MB. URIs exceeding this limit throw an error.

## References
- https://github.com/asymmetric-effort/specifyjs/security/advisories/GHSA-2944-57xv-2682
- https://github.com/asymmetric-effort/specifyjs/commit/25d1fb491d99479efdf501f5f75e0bb80c908f0a
- https://github.com/asymmetric-effort/specifyjs
