# [H] Path traversal in Node-RED-Dashboard

## Summary
Severity: High
Advisory: GHSA-2hw7-mxvj-m455
CVE: CVE-2021-3223
CWE: CWE-22
Ecosystem: npm
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-2hw7-mxvj-m455
Type: github-advisory

## Affected
- npm: `node-red-dashboard` — affected >=0 <2.26.2

## Details
In Node-RED-Dashboard before 2.26.2 there is a path traversal vulnerability. It allows ui_base/js/..%2f directory traversal to read files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3223
- https://github.com/node-red/node-red-dashboard/issues/669
- https://github.com/node-red/node-red-dashboard/commit/f48f356df966f607ba3d09c27396074b81f2ae97
- https://github.com/node-red/node-red-dashboard/releases/tag/2.26.2
- https://www.npmjs.com/package/node-red-dashboard
