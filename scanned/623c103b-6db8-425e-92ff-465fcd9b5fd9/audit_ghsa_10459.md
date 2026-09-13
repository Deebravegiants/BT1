# [H] Electron: Use-after-free in WebContents fullscreen, pointer-lock, and keyboard-lock permission callbacks

## Summary
Severity: High
Advisory: GHSA-8337-3p73-46f4
CVE: CVE-2026-34771
CWE: CWE-416
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-8337-3p73-46f4
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.0
- npm: `electron` — affected >=40.0.0-alpha.1 <40.7.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0-beta.8

## Details
### Impact
Apps that register an asynchronous `session.setPermissionRequestHandler()` may be vulnerable to a use-after-free when handling fullscreen, pointer-lock, or keyboard-lock permission requests. If the requesting frame navigates or the window closes while the permission handler is pending, invoking the stored callback dereferences freed memory, which may lead to a crash or memory corruption.

Apps that do not set a permission request handler, or whose handler responds synchronously, are not affected.

### Workarounds
Respond to permission requests synchronously, or deny fullscreen, pointer-lock, and keyboard-lock requests if an asynchronous flow is required.

### Fixed Versions
* `41.0.0-beta.8`
* `40.7.0`
* `39.8.0`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-8337-3p73-46f4
- https://nvd.nist.gov/vuln/detail/CVE-2026-34771
- https://github.com/electron/electron
