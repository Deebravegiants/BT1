# [M] Electron: ProtocolResponse.url reuses the default session cache instead of the registering session

## Summary
Severity: Medium
Advisory: GHSA-r4w5-6pfg-jxp5
CVE: CVE-2026-70606
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-r4w5-6pfg-jxp5
Type: github-advisory

## Affected
- npm: `electron` — affected >=43.0.0-alpha.1 <43.0.0
- npm: `electron` — affected >=42.0.0-alpha.1 <42.5.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.9.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.10.6

## Details
### Impact
When a custom protocol handler returned a `ProtocolResponse` with a `url` and no `session`, Electron made the upstream request through `defaultSession` instead of the session that handled the protocol. A cached response could then be reused across otherwise isolated session partitions.

Apps that use `ProtocolResponse.url`, omit `ProtocolResponse.session`, and rely on separate sessions to isolate content are affected. Apps that set an explicit `session`, or that do not isolate content across sessions, are not affected.

### Workarounds
Set `ProtocolResponse.session` explicitly so the request uses the intended session's cache.

### Fixed Versions
* `43.0.0`
* `42.5.1`
* `41.9.1`
* `40.10.6`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-r4w5-6pfg-jxp5
- https://github.com/electron/electron
