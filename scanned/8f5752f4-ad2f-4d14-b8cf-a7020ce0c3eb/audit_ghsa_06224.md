# [M] Electron: HTTP redirect followed into local file loader

## Summary
Severity: Medium
Advisory: GHSA-v64r-4m7r-3mvq
CVE: CVE-2026-70605
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-v64r-4m7r-3mvq
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.8
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.1
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.3

## Details
### Impact
When following HTTP redirects, `net.fetch()` and `net.request()` did not restrict which schemes a redirect could target. A remote server could redirect a request to a local resource, and if the app returns or forwards the response body, local file contents could be disclosed.

Apps are only affected if they make `net` requests to attacker-influenced URLs with redirects followed (the default) and expose the response body. Apps that only request fixed, trusted URLs are not affected.

### Workarounds
Set `redirect: 'error'` or `redirect: 'manual'` on requests to untrusted URLs and validate any redirect target before following it.

### Fixed Versions
* `42.0.0-beta.3`
* `41.2.1`
* `40.9.0`
* `39.8.8`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-v64r-4m7r-3mvq
- https://github.com/electron/electron
