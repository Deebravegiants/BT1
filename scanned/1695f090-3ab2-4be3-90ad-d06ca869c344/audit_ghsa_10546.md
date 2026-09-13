# [M] Electron: HTTP Response Header Injection in custom protocol handlers and webRequest

## Summary
Severity: Medium
Advisory: GHSA-4p4r-m79c-wq3v
CVE: CVE-2026-34767
CWE: CWE-113, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-4p4r-m79c-wq3v
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.3
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.3
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.3

## Details
### Impact
Apps that register custom protocol handlers via `protocol.handle()` / `protocol.registerSchemesAsPrivileged()` or modify response headers via `webRequest.onHeadersReceived` may be vulnerable to HTTP response header injection if attacker-controlled input is reflected into a response header name or value.

An attacker who can influence a header value may be able to inject additional response headers, affecting cookies, content security policy, or cross-origin access controls.

Apps that do not reflect external input into response headers are not affected.

### Workarounds
Validate or sanitize any untrusted input before including it in a response header name or value.

### Fixed Versions
* `41.0.3`
* `40.8.3`
* `39.8.3`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, send an email to [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-4p4r-m79c-wq3v
- https://nvd.nist.gov/vuln/detail/CVE-2026-34767
- https://github.com/electron/electron
