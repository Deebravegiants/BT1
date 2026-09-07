# [H] Electron: Context isolation bypass via Function.prototype.bind hijack

## Summary
Severity: High
Advisory: GHSA-h7rp-cf8h-j98x
CVE: CVE-2026-70601
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-h7rp-cf8h-j98x
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.9
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.2
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.2
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.5

## Details
### Impact
Apps that expose Promise-returning functions to web content via `contextBridge` may be vulnerable to a context isolation bypass. Untrusted web content could obtain access to the isolated preload world and, through it, every capability the preload script has. In renderers without a sandbox, or with `nodeIntegration` enabled, this may escalate to Node.js access.

Apps are affected if they expose Promise-returning functions via `contextBridge` — the standard pattern for wrapping `ipcRenderer.invoke` — in windows that load untrusted content. Apps that never load untrusted content in those windows are not affected.

### Workarounds
There are no app side workarounds, you must update to a patched version of Electron.

### Fixed Versions
* `42.0.0-beta.5`
* `41.2.2`
* `40.9.2`
* `39.8.9`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-h7rp-cf8h-j98x
- https://github.com/electron/electron
