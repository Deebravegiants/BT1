# [M] Electron: Named window.open targets not scoped to the opener's browsing context

## Summary
Severity: Medium
Advisory: GHSA-f3pv-wv63-48x8
CVE: CVE-2026-34765
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-f3pv-wv63-48x8
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.5
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.5
- npm: `electron` — affected >=41.0.0-alpha.1 <41.1.0
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-alpha.5

## Details
### Impact
When a renderer calls `window.open()` with a target name, Electron did not correctly scope the named-window lookup to the opener's browsing context group. A renderer could navigate an existing child window that was opened by a different, unrelated renderer if both used the same target name. If that existing child was created with more permissive `webPreferences` (via `setWindowOpenHandler`'s `overrideBrowserWindowOptions`), content loaded by the second renderer inherits those permissions.

Apps are only affected if they open multiple top-level windows with differing trust levels **and** use `setWindowOpenHandler` to grant child windows elevated `webPreferences` such as a privileged preload script. Apps that do not elevate child window privileges, or that use a single top-level window, are not affected.

Apps that additionally grant `nodeIntegration: true` or `sandbox: false` to child windows (contrary to the [security recommendations](https://www.electronjs.org/docs/latest/tutorial/security)) may be exposed to arbitrary code execution.

### Workarounds
Deny `window.open()` in renderers that load untrusted content by returning `{ action: 'deny' }` from `setWindowOpenHandler`. Avoid granting child windows more permissive `webPreferences` than their opener.

### Fixed Versions
* `42.0.0-alpha.5`
* `41.1.0`
* `40.8.5`
* `39.8.5`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-f3pv-wv63-48x8
- https://nvd.nist.gov/vuln/detail/CVE-2026-34765
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v39.8.5
- https://github.com/electron/electron/releases/tag/v40.8.5
- https://github.com/electron/electron/releases/tag/v41.1.0
- https://github.com/electron/electron/releases/tag/v42.0.0-alpha.5
