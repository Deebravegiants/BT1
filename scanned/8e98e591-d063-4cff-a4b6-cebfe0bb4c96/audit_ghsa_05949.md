# [M] Electron: DevTools JavaScript Injection via Unsanitized Dock State Parameter

## Summary
Severity: Medium
Advisory: GHSA-4f78-qhmw-8j8m
CVE: CVE-2026-70609
CWE: CWE-116, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-4f78-qhmw-8j8m
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.7
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.0
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.1

## Details
### Impact
The `mode` option of `webContents.openDevTools()` was not sanitized before use by the DevTools frontend. If an attacker can influence this value, script under their control may run in the DevTools context, which in unsandboxed configurations has access to Node.js.

Apps are only affected if untrusted input can reach the `mode` argument of `openDevTools()`, or if untrusted content can call `openDevTools()` on a `<webview>` it embeds. Apps that only ever pass a fixed dock mode are not affected.

### Workarounds
Only pass fixed, allowlisted values (`right`, `bottom`, `undocked`, `detach`) as the DevTools `mode`, and do not expose `openDevTools` to untrusted content.

### Fixed Versions
* `42.0.0-beta.1`
* `41.2.0`
* `40.9.0`
* `39.8.7`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-4f78-qhmw-8j8m
- https://github.com/electron/electron/pull/50665
- https://github.com/electron/electron/pull/50666
- https://github.com/electron/electron/pull/50667
- https://github.com/electron/electron/pull/50668
- https://github.com/electron/electron/commit/04614eed17986bddc43eb509ec870424ee6a47d1
- https://github.com/electron/electron/commit/2046ae87731d80a7b535512ae19acb529e10e33b
- https://github.com/electron/electron/commit/969741f9f847c5c583f6bbc63ca22549dbd954ce
- https://github.com/electron/electron/commit/efc4d3c6b6f1c04f658ca0d9d2512dcfe78eb7ba
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v39.8.7
- https://github.com/electron/electron/releases/tag/v40.9.0
- https://github.com/electron/electron/releases/tag/v41.2.0
- https://github.com/electron/electron/releases/tag/v42.0.0-beta.1
