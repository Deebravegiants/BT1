# [M] Electron: Service worker can spoof executeJavaScript IPC replies

## Summary
Severity: Medium
Advisory: GHSA-xj5x-m3f3-5x3h
CVE: CVE-2026-34778
CWE: CWE-290, CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-xj5x-m3f3-5x3h
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0

## Details
### Impact
A service worker running in a session could spoof reply messages on the internal IPC channel used by `webContents.executeJavaScript()` and related methods, causing the main-process promise to resolve with attacker-controlled data.

Apps are only affected if they have service workers registered and use the result of `webContents.executeJavaScript()` (or `webFrameMain.executeJavaScript()`) in security-sensitive decisions.

### Workarounds
Do not trust the return value of `webContents.executeJavaScript()` for security decisions. Use dedicated, validated IPC channels for security-relevant communication with renderers.

### Fixed Versions
* `41.0.0`
* `40.8.1`
* `39.8.1`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-xj5x-m3f3-5x3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-34778
- https://github.com/electron/electron
