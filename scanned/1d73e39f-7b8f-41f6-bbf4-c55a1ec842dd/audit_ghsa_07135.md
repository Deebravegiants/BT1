# [M] @asymmetric-effort/specifyjs: Production console warnings may leak internal framework state

## Summary
Severity: Medium
Advisory: GHSA-qcr8-x557-7cp3
CWE: CWE-209
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-qcr8-x557-7cp3
Type: github-advisory

## Affected
- npm: `@asymmetric-effort/specifyjs` — affected >=0 <0.2.140

## Details
## Finding

**Location**: `core/src/core/scheduler.ts:23`, `core/src/hooks/dispatcher.ts:100`, `core/src/client/graphql.ts:71`

Several `console.warn` calls are not gated behind `__DEV__` and will fire in production builds, potentially exposing internal framework state such as queue sizes, component names, and query fragments to users viewing the browser console.

## Status

**Open** — These warnings serve as development-time diagnostics. They do not expose credentials or PII, but may reveal internal architecture details.

## Recommendation

Gate all development-time `console.warn` and `console.error` calls behind `process.env.NODE_ENV !== 'production'` or a `__DEV__` constant that build tools can tree-shake.

## References
- https://github.com/asymmetric-effort/specifyjs/security/advisories/GHSA-qcr8-x557-7cp3
- https://github.com/asymmetric-effort/specifyjs/commit/2ef791bc73ead853efd0c227ad8228bc594a7b63
- https://github.com/asymmetric-effort/specifyjs
