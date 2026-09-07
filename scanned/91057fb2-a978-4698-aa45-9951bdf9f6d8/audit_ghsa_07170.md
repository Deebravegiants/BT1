# [M] hono/jsx does not isolate context per request, leading to cross-request data disclosure

## Summary
Severity: Medium
Advisory: GHSA-hvrm-45r6-mjfj
CVE: CVE-2026-59896
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-hvrm-45r6-mjfj
Type: github-advisory

## Affected
- npm: `hono` — affected >=4.11.8 <4.12.27

## Details
### Summary

`hono/jsx` did not isolate context values per request during server-side rendering. While an async component was suspended on `await`, its provided context value stayed observable to other requests rendering concurrently, so `useContext()` could return a value from a different in-flight request.

### Details

During server-side rendering, context values were kept in a process-wide structure rather than scoped to each request's render. While an async component awaited, another request entering the same provider could observe or replace the value; when the first render resumed, it could read the other request's context.

This affects the usual ways request-scoped data is passed through a server-rendered JSX tree:

- `createContext()` / `useContext()`
- the `jsxRenderer` middleware and `useRequestContext()`

It arises only when context is read after an `await` inside an async component while requests render concurrently. Reading context synchronously (before any `await`), purely synchronous rendering, and client-side (DOM) rendering are not affected.

### Impact

Under concurrent requests, a response could be rendered with another request's context. A user may receive HTML rendered for a different user, and an authorization check performed after an `await` may be evaluated against another user's data.

This may lead to:

- disclosure of rendered output intended for another user
- authorization decisions made with the wrong request's context
- cross-request mixing of session or other request-scoped state

## References
- https://github.com/honojs/hono/security/advisories/GHSA-hvrm-45r6-mjfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-59896
- https://github.com/honojs/hono/commit/fab3b13639339cbd5ba1166a5b23d9ac30c5f64f
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.27
