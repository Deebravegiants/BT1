# [M] React Router has CSRF issue in Action/Server Action Request Processing

## Summary
Severity: Medium
Advisory: GHSA-h5cw-625j-3rxh
CVE: CVE-2026-22030
CWE: CWE-346, CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-h5cw-625j-3rxh
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.12.0
- npm: `@remix-run/server-runtime` — affected >=0 <2.17.3

## Details
React Router (or Remix v2) is vulnerable to CSRF attacks on document POST requests to UI routes when using server-side route `action` handlers in [Framework Mode](https://reactrouter.com/start/modes#framework), or when using React Server Actions in the new unstable RSC modes.

> [!NOTE]
> This does not impact your application if you are using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`) or [Data Mode](https://reactrouter.com/start/modes#data) (`createBrowserRouter`/`<RouterProvider>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-h5cw-625j-3rxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-22030
- https://github.com/remix-run/react-router
