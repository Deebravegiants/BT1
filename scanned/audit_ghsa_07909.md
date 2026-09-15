# [M] @farmfe/core is Missing Origin Validation in WebSocket

## Summary
Severity: Medium
Advisory: GHSA-p773-8mf4-rjm5
CVE: CVE-2025-56647
CWE: CWE-1385
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-12
Source: https://github.com/advisories/GHSA-p773-8mf4-rjm5
Type: github-advisory

## Affected
- npm: `@farmfe/core` — affected >=0 <1.7.6

## Details
npm @farmfe/core before 1.7.6 is Missing Origin Validation in WebSocket. The development (hot module reloading) server does not validate origin when connecting to a WebSocket client. This allows attackers to surveil developers running Farm who visit their webpage and steal source code that is leaked by the WebSocket server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56647
- https://github.com/farm-fe/farm/issues/2168
- https://github.com/farm-fe/farm/commit/83342ef06e0aea37270950fd8c930422c4df0679
- https://gist.github.com/R4356th/d4372c6f83275d583c180c0e7d7332af
- https://github.com/farm-fe/farm
