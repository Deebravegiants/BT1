# [M] Hono: `memo()` retains SSR output across requests, leading to cross-user data disclosure

## Summary
Severity: Medium
Advisory: GHSA-f23p-vx2j-j53r
CVE: CVE-2026-71850
CWE: CWE-488
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-f23p-vx2j-j53r
Type: github-advisory

## Affected
- npm: `hono` — affected >=3.8.0 <4.12.34

## Details
### Summary

`memo()` from `hono/jsx` retains the result of a server-side render and reuses it for later renders with comparator-equal props. Request-scoped values read inside the component take no part in that comparison, so a response can contain HTML rendered for another user's request.

### Details

Components wrapped with `memo()` are compared by props alone. Values read implicitly during rendering do not participate: JSX Context through `createContext()` and `useContext()`, `useRequestContext()` from `hono/jsx-renderer`, and `getContext()` from `hono/context-storage`. The retained result lives as long as the wrapped component, so it outlives the request that produced it.

Per-request context isolation is not what fails: the current request's values are established correctly, but the memoized component is skipped before anything reads them.

This issue arises when a component wrapped in `memo()` obtains user- or request-specific data from an ambient context instead of through props.

### Impact

A user may receive a response containing HTML rendered for another user, when both render the same memoized component with comparator-equal props on the same warm instance.

This may lead to:

- Disclosure of another user's account or profile data
- Disclosure of request-scoped secrets embedded in HTML, such as CSRF tokens
- Exposure of role-specific content to users who should not receive it

Exploitation depends on the order in which renders populate the retained value and on both requests reaching the same warm instance.

This issue affects applications that render with `hono/jsx` on the server and wrap a component reading ambient request state in `memo()`. Applications that pass all request-specific values through props, or that do not use `memo()`, are unaffected. Client-side rendering is unaffected.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-f23p-vx2j-j53r
- https://github.com/honojs/hono/commit/0c45036d6b0ddf42ab2fa44639dc8710825d5c0f
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.34
