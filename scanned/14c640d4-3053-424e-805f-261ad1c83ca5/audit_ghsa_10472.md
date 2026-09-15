# [H] Electron: Use-after-free in offscreen child window paint callback

## Summary
Severity: High
Advisory: GHSA-532v-xpq5-8h95
CVE: CVE-2026-34774
CWE: CWE-416
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-532v-xpq5-8h95
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.7.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0

## Details
### Impact
Apps that use offscreen rendering and allow child windows via `window.open()` may be vulnerable to a use-after-free. If the parent offscreen `WebContents` is destroyed while a child window remains open, subsequent paint frames on the child dereference freed memory, which may lead to a crash or memory corruption.

Apps are only affected if they use offscreen rendering (`webPreferences.offscreen: true`) and their `setWindowOpenHandler` permits child windows. Apps that do not use offscreen rendering, or that deny child windows, are not affected.

### Workarounds
Deny child window creation from offscreen renderers in your `setWindowOpenHandler`, or ensure child windows are closed before the parent is destroyed.

### Fixed Versions
* `41.0.0`
* `40.7.0`
* `39.8.1`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-532v-xpq5-8h95
- https://nvd.nist.gov/vuln/detail/CVE-2026-34774
- https://github.com/electron/electron
