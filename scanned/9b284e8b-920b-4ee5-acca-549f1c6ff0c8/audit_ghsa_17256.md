# [H] Servify-express rate limit issue

## Summary
Severity: High
Advisory: GHSA-qgc4-8p88-4w7m
CVE: CVE-2025-67731
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-11
Source: https://github.com/advisories/GHSA-qgc4-8p88-4w7m
Type: github-advisory

## Affected
- npm: `servify-express` — affected >=0 <1.2

## Details
### Impact
The Express server uses `express.json()` without a size limit, which can allow attackers to send extremely large request bodies. This may lead to excessive memory usage, degraded performance, or process crashes, resulting in a Denial of Service (DoS). Any application using the JSON parser without limits and exposed to untrusted clients is affected.

### Patches
This issue is not a flaw in Express itself but in configuration. Users should set a request-size limit when enabling the JSON body parser. For example:
`app.use(express.json({ limit: "100kb" }));`

### Workarounds
Users can mitigate the issue without upgrading by:
- Adding a `limit` option to the JSON parser
- Implementing rate limiting at the application or reverse-proxy level
- Rejecting unusually large requests before parsing
- Using a reverse proxy (such as NGINX) to enforce maximum request body sizes

## References
- https://github.com/Aarondoran/servify-express/security/advisories/GHSA-qgc4-8p88-4w7m
- https://nvd.nist.gov/vuln/detail/CVE-2025-67731
- https://github.com/Aarondoran/servify-express/commit/197d848e5450bf85b0dd19ef8c2aa4ba96192300
- https://github.com/Aarondoran/servify-express/commit/8dff7f56504b356278d849734ef2050e5cd23b61
- https://github.com/Aarondoran/servify-express
- https://github.com/Aarondoran/servify-express/releases/tag/V1.2
