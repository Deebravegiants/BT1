# [M] React Router has stored XSS via unescaped Location header in prerendered redirect HTML

## Summary
Severity: Medium
Advisory: GHSA-f22v-gfqf-p8f3
CVE: CVE-2026-33244
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-f22v-gfqf-p8f3
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.5.1 <7.13.2

## Details
When using React Router v7 [Framework Mode](https://reactrouter.com/start/modes#framework) with [Pre-rendering](https://reactrouter.com/how-to/pre-rendering) enabled, an improper neutralization of the HTTP `Location` header value can permit Cross-Site Scripting (XSS) in statically generated HTML files if the redirect location comes from an untrusted source.

> [!NOTE]
> This does not impact your React Router application if you are using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`) or [Data Mode](https://reactrouter.com/start/modes#data) (`createBrowserRouter`/`<RouterProvider>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-f22v-gfqf-p8f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33244
- https://github.com/remix-run/react-router
