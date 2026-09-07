# [H] React Router has XSS Vulnerability

## Summary
Severity: High
Advisory: GHSA-3cgp-3xvw-98x8
CVE: CVE-2025-59057
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-3cgp-3xvw-98x8
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.9.0
- npm: `@remix-run/react` — affected >=1.15.0 <2.17.1

## Details
A XSS vulnerability exists in in React Router's `meta()`/`<Meta>` APIs in [Framework Mode](https://reactrouter.com/start/modes#framework) when generating `script:ld+json` tags which could allow arbitrary JavaScript execution during SSR if untrusted content is used to generate the tag.

> [!NOTE]
> This does not impact applications using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`) or [Data Mode](https://reactrouter.com/start/modes#data) (`createBrowserRouter`/`<RouterProvider>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-3cgp-3xvw-98x8
- https://nvd.nist.gov/vuln/detail/CVE-2025-59057
- https://github.com/remix-run/react-router
