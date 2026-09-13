# [M] Electron: window.open features string controls some window options considered privileged

## Summary
Severity: Medium
Advisory: GHSA-v93f-fgjr-hjrj
CVE: CVE-2026-70607
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-v93f-fgjr-hjrj
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.8
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.1
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.3

## Details
### Impact
Some window options supplied by web content in the `window.open()` features string were applied to the new `BrowserWindow` without an allowlist. Untrusted content could set window options it should not control, including options that cause the main process to access attacker-chosen file or network paths.

Apps are only affected if untrusted content can call `window.open()` and the app does not override child window options via `setWindowOpenHandler`. Apps that deny `window.open()` for untrusted content, or set `overrideBrowserWindowOptions` explicitly, are not affected.

### Workarounds
Return `{ action: 'deny' }` from `setWindowOpenHandler` for untrusted content, or supply `overrideBrowserWindowOptions` so every window option is set explicitly.

### Fixed Versions
* `42.0.0-beta.3`
* `41.2.1`
* `40.9.0`
* `39.8.8`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-v93f-fgjr-hjrj
- https://github.com/electron/electron/pull/50946
- https://github.com/electron/electron/pull/50947
- https://github.com/electron/electron/pull/50948
- https://github.com/electron/electron/pull/50949
- https://github.com/electron/electron/commit/30cf3882de75ee651bd4e5f27002f13fd3d3163a
- https://github.com/electron/electron/commit/4eff3dc09e4d1e62d649c5ce9902f532bb7469c7
- https://github.com/electron/electron/commit/615d62500fc7732d068274b796c49487e652e90b
- https://github.com/electron/electron/commit/fe2e7d0073949b4593b624b93abf1788f5377e55
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v39.8.8
- https://github.com/electron/electron/releases/tag/v40.9.0
- https://github.com/electron/electron/releases/tag/v41.2.1
- https://github.com/electron/electron/releases/tag/v42.0.0-beta.3
