# [H] React Router's vendored turbo-stream v2 allows arbitrary constructor invocation via TYPE_ERROR deserialization leading to Unauth RCE

## Summary
Severity: High
Advisory: GHSA-49rj-9fvp-4h2h
CVE: CVE-2026-42211
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-49rj-9fvp-4h2h
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.14.2

## Details
When using React Router v7 in [Framework Mode](https://reactrouter.com/start/modes#framework), there exists a combination of steps that could potentially allow unauthorized RCE through external requests.  This first requires the application code to have an existing prototype pollution vulnerability.  This can be leveraged into a 2-step attack in which the second step can trigger unauthorized RCE on the remote server.

> [!NOTE]
> This does not impact your React Router application if you are using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`) or [Data Mode](https://reactrouter.com/start/modes#data) (`createBrowserRouter`/`<RouterProvider>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-49rj-9fvp-4h2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42211
- https://github.com/remix-run/react-router
