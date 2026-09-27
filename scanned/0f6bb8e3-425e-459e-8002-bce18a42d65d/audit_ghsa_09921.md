# [M] Electron: Use-after-free in download save dialog callback

## Summary
Severity: Medium
Advisory: GHSA-9w97-2464-8783
CVE: CVE-2026-34772
CWE: CWE-416
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-9w97-2464-8783
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.0
- npm: `electron` — affected >=40.0.0-alpha.1 <40.7.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0-beta.7

## Details
### Impact
Apps that allow downloads and programmatically destroy sessions may be vulnerable to a use-after-free. If a session is torn down while a native save-file dialog is open for a download, dismissing the dialog dereferences freed memory, which may lead to a crash or memory corruption.

Apps that do not destroy sessions at runtime, or that do not permit downloads, are not affected.

### Workarounds
Avoid destroying sessions while a download save dialog may be open. Cancel pending downloads before session teardown.

### Fixed Versions
* `41.0.0-beta.7`
* `40.7.0`
* `39.8.0`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-9w97-2464-8783
- https://nvd.nist.gov/vuln/detail/CVE-2026-34772
- https://github.com/electron/electron
