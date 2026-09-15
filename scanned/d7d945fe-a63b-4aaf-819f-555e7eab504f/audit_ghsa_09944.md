# [M] Electron: AppleScript injection in app.moveToApplicationsFolder on macOS

## Summary
Severity: Medium
Advisory: GHSA-5rqw-r77c-jp79
CVE: CVE-2026-34779
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-5rqw-r77c-jp79
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0-beta.8

## Details
### Impact
On macOS, `app.moveToApplicationsFolder()` used an AppleScript fallback path that did not properly handle certain characters in the application bundle path. Under specific conditions, a crafted launch path could lead to arbitrary AppleScript execution when the user accepted the move-to-Applications prompt.

Apps are only affected if they call `app.moveToApplicationsFolder()`. Apps that do not use this API are not affected.

### Workarounds
There are no app side workarounds, developers must update to a patched version of Electron.

### Fixed Versions
* `41.0.0-beta.8`
* `40.8.0`
* `39.8.1`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-5rqw-r77c-jp79
- https://nvd.nist.gov/vuln/detail/CVE-2026-34779
- https://github.com/electron/electron
