# [M] Electron has ASAR Integrity Bypass via resource modification

## Summary
Severity: Medium
Advisory: GHSA-vmqv-hx8q-j7mg
CVE: CVE-2025-55305
CWE: CWE-829, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-vmqv-hx8q-j7mg
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <35.7.5
- npm: `electron` — affected >=36.0.0-alpha.1 <36.8.1
- npm: `electron` — affected >=37.0.0-alpha.1 <37.3.1
- npm: `electron` — affected >=38.0.0-alpha.1 <38.0.0-beta.6

## Details
### Impact
This only impacts apps that have the `embeddedAsarIntegrityValidation` and `onlyLoadAppFromAsar` [fuses](https://www.electronjs.org/docs/latest/tutorial/fuses) enabled.  Apps without these fuses enabled are not impacted.

Specifically this issue can only be exploited if your app is launched from a filesystem the attacker has write access too.  i.e. the ability to edit files inside the `resources` folder in your app installation on Windows which these fuses are supposed to protect against.

### Workarounds
There are no app side workarounds, you must update to a patched version of Electron.

### Fixed Versions
* `38.0.0-beta.6`
* `37.3.1`
* `36.8.1`
* `35.7.5`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-vmqv-hx8q-j7mg
- https://nvd.nist.gov/vuln/detail/CVE-2025-55305
- https://github.com/electron/electron/pull/48101
- https://github.com/electron/electron/pull/48102
- https://github.com/electron/electron/pull/48103
- https://github.com/electron/electron/pull/48104
- https://github.com/electron/electron/commit/23a02934510fcf951428e14573d9b2d2a3c4f28b
- https://github.com/electron/electron/commit/2e5a0b7220ebf955c6785cc5adb2e2b1cf77dac1
- https://github.com/electron/electron/commit/3f92511cdecc39f46b0e86cce40a0c691e301c9d
- https://github.com/electron/electron/commit/fdf29ce83870109d403f5c23ae529dbd0e8f4fee
- https://github.com/electron/electron
