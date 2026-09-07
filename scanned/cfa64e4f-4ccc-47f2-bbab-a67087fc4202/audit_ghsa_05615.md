# [H] React Router SSR XSS in ScrollRestoration

## Summary
Severity: High
Advisory: GHSA-8v8x-cx79-35w7
CVE: CVE-2026-21884
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-8v8x-cx79-35w7
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.12.0
- npm: `@remix-run/react` — affected >=0 <2.17.3

## Details
A XSS vulnerability exists in in React Router's `<ScrollRestoration>` API in [Framework Mode](https://reactrouter.com/start/modes#framework) when using the `getKey`/`storageKey` props during Server-Side Rendering which could allow arbitrary JavaScript execution during SSR if untrusted content is used to generate the keys.

> [!NOTE]
> This does not impact applications if developers have [disabled server-side rendering](https://reactrouter.com/how-to/spa) in Framework Mode, or if they are using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`) or [Data Mode](https://reactrouter.com/start/modes#data) (`createBrowserRouter`/`<RouterProvider>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-8v8x-cx79-35w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-21884
- https://github.com/remix-run/react-router
