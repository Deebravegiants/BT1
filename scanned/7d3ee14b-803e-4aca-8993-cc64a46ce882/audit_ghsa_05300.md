# [H] React Router vulnerable to Denial of Service via reflected user input in single-fetch

## Summary
Severity: High
Advisory: GHSA-rxv8-25v2-qmq8
CVE: CVE-2026-34077
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-rxv8-25v2-qmq8
Type: github-advisory

## Affected
- npm: `react-router` — affected >=7.0.0 <7.14.0
- npm: `turbo-stream` — affected >=0 <3.0.0

## Details
A DoS vulnerability exists in the React Router v7 [Framework Mode](https://reactrouter.com/start/modes#framework), as well as Remix v2.9.0+ with [Single Fetch](https://v2.remix.run/docs/guides/single-fetch) enabled. In some scenarios the underlying serialization algorithm can become a bottleneck when encoding specific types of data into server responses.  Please upgrade to React Router v7.14.0 or later.

> [!NOTE]
> This does not impact your React Router application if you are using [Declarative Mode](https://reactrouter.com/start/modes#declarative) (`<BrowserRouter>`) or [Data Mode](https://reactrouter.com/start/modes#data) (`createBrowserRouter`/`<RouterProvider>`).

## References
- https://github.com/remix-run/react-router/security/advisories/GHSA-rxv8-25v2-qmq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-34077
- https://github.com/remix-run/react-router/commit/59811921d3c7d599077b8cadccdcd65a233165e0
- https://github.com/jacob-ebey/turbo-stream/blob/v2.4.1/src/flatten.ts#L175-L177
- https://github.com/jacob-ebey/turbo-stream/blob/v2.4.1/src/unflatten.ts#L185-L189
- https://github.com/remix-run/react-router
