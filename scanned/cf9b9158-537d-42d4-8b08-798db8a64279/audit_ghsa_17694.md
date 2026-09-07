# [H] electron ASAR Integrity bypass by just modifying the content

## Summary
Severity: High
Advisory: GHSA-xw5q-g62x-2qjc
CVE: CVE-2024-46992
CWE: CWE-354
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-xw5q-g62x-2qjc
Type: github-advisory

## Affected
- npm: `electron` — affected >=30.0.0-alpha.1 <30.0.5
- npm: `electron` — affected >=31.0.0-alpha.1 <31.0.0-beta.1

## Details
electron's ASAR Integrity can be bypass by modifying the content.

### Impact
This only impacts apps that have the `embeddedAsarIntegrityValidation` and `onlyLoadAppFromAsar` [fuses](https://www.electronjs.org/docs/latest/tutorial/fuses) enabled. Apps without these fuses enabled are not impacted. This issue is specific to Windows, apps using these fuses on macOS are unimpacted.

Specifically this issue can only be exploited if your app is launched from a filesystem the attacker has write access too. i.e. the ability to edit files inside the .app bundle on macOS which these fuses are supposed to protect against.

### Workarounds
There are no app side workarounds, you must update to a patched version of Electron.

### Fixed Versions
* `30.0.5`
* `31.0.0-beta.1`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-xw5q-g62x-2qjc
- https://nvd.nist.gov/vuln/detail/CVE-2024-46992
- https://github.com/electron/electron
- https://www.electronjs.org/docs/latest/tutorial/fuses
