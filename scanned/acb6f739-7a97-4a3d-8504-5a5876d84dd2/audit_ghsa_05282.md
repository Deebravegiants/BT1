# [M] React Router's same-origin redirect with path starting // causes open redirect via protocol-relative URL reinterpretation

## Summary
Severity: Medium
Advisory: GHSA-2j2x-hqr9-3h42
CVE: CVE-2026-40181
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-2j2x-hqr9-3h42
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.14.1
- npm: `react-router` — affected >=6.7.0 <6.30.4
- npm: `@remix-run/router` — affected >=1.3.0 <1.23.3

## Details
Certain URLs passed to the `redirect` function can trigger an open redirect to an external domain depending on the level of validation done by the application prior to returning the `redirect`.

> [!NOTE]
> This does not impact your React Router application if you are using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`)

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-2j2x-hqr9-3h42
- https://nvd.nist.gov/vuln/detail/CVE-2026-40181
- https://github.com/remix-run/react-router/commit/d77f6b1
- https://github.com/remix-run/react-router
