# [H] React Router vulnerable to XSS via Open Redirects

## Summary
Severity: High
Advisory: GHSA-2w69-qvjg-hvjx
CVE: CVE-2026-22029
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-2w69-qvjg-hvjx
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.12.0
- npm: `@remix-run/router` — affected >=0 <1.23.2

## Details
React Router (and Remix v1/v2) SPA open navigation redirects originating from loaders or actions in [Framework Mode](https://reactrouter.com/start/modes#framework), [Data Mode](https://reactrouter.com/start/modes#data), or the unstable RSC modes can result in unsafe URLs causing unintended javascript execution on the client. This is only an issue if developers are creating redirect paths from untrusted content or via an open redirect.

> [!NOTE]
> This does not impact applications that use [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-2w69-qvjg-hvjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-22029
- https://github.com/remix-run/react-router
