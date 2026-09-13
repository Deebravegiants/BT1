# [H] React Router: Unauthenticated Denial of Service via Inefficient Route Matching

## Summary
Severity: High
Advisory: GHSA-chx6-hx7r-mcp5
CVE: CVE-2026-55685
CWE: CWE-400, CWE-407
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-chx6-hx7r-mcp5
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.18.0

## Details
This is a follow up to https://github.com/remix-run/react-router/security/advisories/GHSA-8x6r-g9mw-2r78 that covers additional reported scenarios in which the manifest endpoint could be accessed via unauthenticated targeted requests that would put heavy load on the server and slow down response times.

> [!NOTE]
> This only impacts Framework Mode applications.  This does not impact your application if you are using Declarative or Data Mode.

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-chx6-hx7r-mcp5
- https://github.com/remix-run/react-router/pull/15186
- https://github.com/remix-run/react-router/commit/09e6020d1950e54f361f7ad00938ecd4dde60929
- https://github.com/remix-run/react-router
- https://github.com/remix-run/react-router/blob/main/CHANGELOG.md#v7180
- https://github.com/remix-run/react-router/releases/tag/react-router@7.18.0
