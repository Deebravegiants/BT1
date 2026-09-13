# [M] Electron: shell.openPath path validation bypass via embedded null byte

## Summary
Severity: Medium
Advisory: GHSA-5c9j-mhmv-5xgx
CVE: CVE-2026-70603
CWE: CWE-158, CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-5c9j-mhmv-5xgx
Type: github-advisory

## Affected
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.1
- npm: `electron` — affected >=41.0.0-alpha.1 <41.1.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.0
- npm: `electron` — affected >=0 <39.8.6

## Details
### Impact
`shell.openPath()` did not reject paths containing embedded null bytes. Apps that perform string-only validation of file paths (for example, checking the file extension) before passing them to `shell.openPath()` could be bypassed, allowing an attacker-controlled path to open a different file than the one that passed validation.

Apps are only affected if they pass paths derived from untrusted input to `shell.openPath()` and rely on string-based validation without a filesystem check. Node's `fs` APIs already reject paths containing null bytes, so apps that call `fs.existsSync()`, `fs.stat()`, or similar before `shell.openPath()` are not affected. Apps that do not call `shell.openPath()` with untrusted input are not affected.

### Workarounds
Reject any path containing a null byte before passing it to `shell.openPath()`:
```js
if (filePath.includes('\0')) throw new Error('invalid path');
```

### Fixed Versions
* `42.0.0-beta.1`
* `41.1.1`
* `40.9.0`
* `39.8.6`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-5c9j-mhmv-5xgx
- https://github.com/electron/electron
