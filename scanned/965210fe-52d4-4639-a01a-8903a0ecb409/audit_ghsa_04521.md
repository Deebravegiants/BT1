# [H] React Router vulnerable to DoS via unbounded path expansion in __manifest endpoint

## Summary
Severity: High
Advisory: GHSA-8x6r-g9mw-2r78
CVE: CVE-2026-42342
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-8x6r-g9mw-2r78
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.15.0
- npm: `@remix-run/server-runtime` — affected >=2.10.0 <2.17.5

## Details
There exists a potential DOS attack vector in React Router Framework Mode applications (as well as Remix v2.10.0 - 2.17.4).  Certain requests can be crafted to consume disproportionate resources on the server, resulting in response time degredation and/or service unavailability for end users.

> [!NOTE]
> This does not impact your React Router application if you are using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`) or [Data Mode](https://reactrouter.com/start/modes#data) (`createBrowserRouter`/`<RouterProvider>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-8x6r-g9mw-2r78
- https://nvd.nist.gov/vuln/detail/CVE-2026-42342
- https://github.com/remix-run/react-router
