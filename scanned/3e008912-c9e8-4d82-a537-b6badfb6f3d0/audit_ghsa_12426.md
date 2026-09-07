# [M] ASAR Integrity bypass via filetype confusion in electron

## Summary
Severity: Medium
Advisory: GHSA-7m48-wc93-9g85
CVE: CVE-2023-44402
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2023-12-01
Source: https://github.com/advisories/GHSA-7m48-wc93-9g85
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <22.3.24
- npm: `electron` — affected >=24.0.0-alpha.1 <24.8.3
- npm: `electron` — affected >=25.0.0-alpha.1 <25.8.1
- npm: `electron` — affected >=26.0.0-alpha.1 <26.2.1
- npm: `electron` — affected >=27.0.0-alpha.1 <27.0.0-alpha.7
- npm: `electron` — affected >=23.0.0-alpha.1

## Details
### Impact
This only impacts apps that have the `embeddedAsarIntegrityValidation` and `onlyLoadAppFromAsar` [fuses](https://www.electronjs.org/docs/latest/tutorial/fuses) enabled.  Apps without these fuses enabled are not impacted.  This issue is specific to macOS as these fuses are only currently supported on macOS.

Specifically this issue can only be exploited if your app is launched from a filesystem the attacker has write access too.  i.e. the ability to edit files inside the `resources` folder in your app installation on Windows which these fuses are supposed to protect against.

### Workarounds
There are no app side workarounds, you must update to a patched version of Electron.

### Fixed Versions
* `27.0.0-alpha.7`
* `26.2.1`
* `25.8.1`
* `24.8.3`
* `22.3.24`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-7m48-wc93-9g85
- https://nvd.nist.gov/vuln/detail/CVE-2023-44402
- https://github.com/electron/electron/pull/39788
- https://github.com/electron/electron
- https://www.electronjs.org/docs/latest/tutorial/fuses
