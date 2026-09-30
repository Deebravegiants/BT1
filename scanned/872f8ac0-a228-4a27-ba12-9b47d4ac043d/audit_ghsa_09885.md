# [M] Electron: Out-of-bounds read in second-instance IPC on macOS and Linux

## Summary
Severity: Medium
Advisory: GHSA-3c8v-cfp5-9885
CVE: CVE-2026-34776
CWE: CWE-125
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-3c8v-cfp5-9885
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0

## Details
### Impact
On macOS and Linux, apps that call `app.requestSingleInstanceLock()` were vulnerable to an out-of-bounds heap read when parsing a crafted second-instance message. Leaked memory could be delivered to the app's `second-instance` event handler.

This issue is limited to processes running as the same user as the Electron app.

Apps that do not call `app.requestSingleInstanceLock()` are not affected. Windows is not affected by this issue.

### Workarounds
There are no app side workarounds, developers must update to a patched version of Electron.

### Fixed Versions
* `41.0.0`
* `40.8.1`
* `39.8.1`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-3c8v-cfp5-9885
- https://nvd.nist.gov/vuln/detail/CVE-2026-34776
- https://github.com/electron/electron
