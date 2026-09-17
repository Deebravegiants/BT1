# [M] Electron: Incorrect origin passed to permission request handler for iframe requests

## Summary
Severity: Medium
Advisory: GHSA-r5p7-gp4j-qhrx
CVE: CVE-2026-34777
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-r5p7-gp4j-qhrx
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0

## Details
### Impact
When an iframe requests `fullscreen`, `pointerLock`, `keyboardLock`, `openExternal`, or `media` permissions, the origin passed to `session.setPermissionRequestHandler()` was the top-level page's origin rather than the requesting iframe's origin. Apps that grant permissions based on the origin parameter or `webContents.getURL()` may inadvertently grant permissions to embedded third-party content.

The correct requesting URL remains available via `details.requestingUrl`. Apps that already check `details.requestingUrl` are not affected.

### Workarounds
In your `setPermissionRequestHandler`, inspect `details.requestingUrl` rather than the origin parameter or `webContents.getURL()` when deciding whether to grant `fullscreen`, `pointerLock`, `keyboardLock`, `openExternal`, or `media` permissions.

### Fixed Versions
* `41.0.0`
* `40.8.1`
* `39.8.1`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-r5p7-gp4j-qhrx
- https://nvd.nist.gov/vuln/detail/CVE-2026-34777
- https://github.com/electron/electron
