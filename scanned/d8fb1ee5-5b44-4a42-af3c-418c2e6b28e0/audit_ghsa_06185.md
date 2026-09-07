# [M] Electron: Parent process code-sign check is spoofable

## Summary
Severity: Medium
Advisory: GHSA-jm7p-cc5g-qwxx
CVE: CVE-2026-70597
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-jm7p-cc5g-qwxx
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.8
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.1
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.3

## Details
### Impact
On macOS, the check Electron uses to confirm it was launched by a same-signed parent process could be bypassed by a local process. Apps that enable the fuse-based hardening restricting `ELECTRON_RUN_AS_NODE` and `NODE_OPTIONS` to same-signed parents rely on this check; a local attacker could bypass it and run their own code inside the signed app, inheriting its TCC permissions and keychain access.

Apps are only affected if they enable those macOS fuse-based restrictions. Apps that do not enable them are not affected.

### Workarounds
There are no app side workarounds, you must update to a patched version of Electron.

### Fixed Versions
* `42.0.0-beta.3`
* `41.2.1`
* `40.9.0`
* `39.8.8`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-jm7p-cc5g-qwxx
- https://github.com/electron/electron/commit/0a6291a97d210db3733689e70a51f5711e38ed35
- https://github.com/electron/electron
