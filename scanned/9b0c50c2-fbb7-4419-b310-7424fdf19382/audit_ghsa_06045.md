# [M] Electron: Extension tab APIs operate across session boundaries

## Summary
Severity: Medium
Advisory: GHSA-m55f-7gqj-fr98
CVE: CVE-2026-70602
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-m55f-7gqj-fr98
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.8
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.1
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.3

## Details
### Impact
Extension tab and scripting APIs were not scoped to the extension's own `session`. A malicious or compromised extension loaded into one session could navigate, script, and read from windows belonging to a different session.

Apps are only affected if they load Chrome extensions via `session.loadExtension` and rely on separate sessions to isolate that extension from other content. Apps that do not load extensions, or that use a single session, are not affected.

### Workarounds
Only load extensions from sources you trust; do not rely on session separation alone to contain an extension.

### Fixed Versions
* `42.0.0-beta.3`
* `41.2.1`
* `40.9.0`
* `39.8.8`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-m55f-7gqj-fr98
- https://github.com/electron/electron
