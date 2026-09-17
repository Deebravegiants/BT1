# [H] Electron: Custom protocol with supportFetchAPI but not corsEnabled allows cross-origin reads

## Summary
Severity: High
Advisory: GHSA-v3j7-r9gq-3gjw
CVE: CVE-2026-70604
CWE: CWE-942
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-v3j7-r9gq-3gjw
Type: github-advisory

## Affected
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.4.0
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.3
- npm: `electron` — affected >=0 <39.8.10

## Details
### Impact
A custom scheme registered with `supportFetchAPI: true` but without `corsEnabled: true` was not subject to CORS enforcement. A page loaded from a remote origin could therefore `fetch()` or `XMLHttpRequest` that scheme cross-origin and read the full response body, rather than the read being blocked.

Apps that serve sensitive data from such a scheme and load remote or untrusted content in a renderer are affected. Apps that set `corsEnabled: true`, or that do not load untrusted content, are not affected.

### Workarounds
Set `corsEnabled: true` on schemes that must enforce CORS, and validate the request `Origin` in your protocol handler before returning sensitive data.

### Fixed Versions
* `42.0.0`
* `41.4.0`
* `40.9.3`
* `39.8.10`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-v3j7-r9gq-3gjw
- https://github.com/electron/electron
