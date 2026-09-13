# [H] Electron: Renderer command-line switch injection via undocumented commandLineSwitches webPreference

## Summary
Severity: High
Advisory: GHSA-9wfr-w7mm-pc7f
CVE: CVE-2026-34769
CWE: CWE-88, CWE-912
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-9wfr-w7mm-pc7f
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.0
- npm: `electron` — affected >=40.0.0-alpha.1 <40.7.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0-beta.8

## Details
### Impact
An undocumented `commandLineSwitches` webPreference allowed arbitrary switches to be appended to the renderer process command line. Apps that construct `webPreferences` by spreading untrusted configuration objects may inadvertently allow an attacker to inject switches that disable renderer sandboxing or web security controls.

Apps are only affected if they construct `webPreferences` from external or untrusted input without an allowlist. Apps that use a fixed, hardcoded `webPreferences` object are not affected.

### Workarounds
Do not spread untrusted input into `webPreferences`. Use an explicit allowlist of permitted preference keys when constructing `BrowserWindow` or `webContents` options from external configuration.

### Fixed Versions
* `41.0.0-beta.8`
* `40.7.0`
* `39.8.0`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, send an email to [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-9wfr-w7mm-pc7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34769
- https://github.com/electron/electron
