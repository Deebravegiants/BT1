# [H] Context isolation bypass via contextBridge in Electron

## Summary
Severity: High
Advisory: GHSA-h9jc-284h-533g
CVE: CVE-2020-4077
CWE: CWE-501
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-07
Source: https://github.com/advisories/GHSA-h9jc-284h-533g
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <7.2.4
- npm: `electron` — affected >=8.0.0 <8.2.4

## Details
### Impact
Apps using both `contextIsolation` and `contextBridge` are affected.

This is a context isolation bypass, meaning that code running in the main world context in the renderer can reach into the isolated Electron context and perform privileged actions.

### Workarounds
There are no app-side workarounds, you must update your Electron version to be protected.

### Fixed Versions
* `9.0.0-beta.21`
* `8.2.4`
* `7.2.4`

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-h9jc-284h-533g
- https://nvd.nist.gov/vuln/detail/CVE-2020-4077
- https://github.com/electron/electron/commit/b8e347709245d2dc5640fbb3044d9b21b4eaa6b0
- https://www.electronjs.org/releases/stable?page=3#release-notes-for-v824
