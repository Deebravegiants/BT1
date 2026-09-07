# [M] Electron: Sandboxed iframes can launch external protocol handlers

## Summary
Severity: Medium
Advisory: GHSA-p2rr-rvmm-c5fp
CVE: CVE-2026-70612
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-p2rr-rvmm-c5fp
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.8
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.1
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.3

## Details
### Impact
Requests to open external protocol URLs from web content did not take iframe sandbox restrictions into account, so a sandboxed iframe could cause an OS-registered external application to be launched. The frame's sandbox state was also not made available to the app's permission handlers.

Apps are only affected if they render untrusted content in sandboxed iframes and grant the `openExternal` permission (granted by default when no `setPermissionRequestHandler` is installed). Apps whose permission handler denies `openExternal` for untrusted content are not affected.

### Workarounds
Install a `setPermissionRequestHandler` that denies the `openExternal` permission for untrusted content.

### Fixed Versions
* `42.0.0-beta.3`
* `41.2.1`
* `40.9.0`
* `39.8.8`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-p2rr-rvmm-c5fp
- https://github.com/electron/electron/pull/50961
- https://github.com/electron/electron/pull/50962
- https://github.com/electron/electron/pull/50963
- https://github.com/electron/electron/pull/50964
- https://github.com/electron/electron/commit/08b9d0a220e267d1a2402a44bdd01a2e9aa320b5
- https://github.com/electron/electron/commit/2764e4c35168855f614876051823db4f58a3714a
- https://github.com/electron/electron/commit/477dcf7afc6550715f9ec5e6f39ee38e5dd7bf39
- https://github.com/electron/electron/commit/c39e3d5687d57434c8d5fe814c5152efd2f631c3
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v39.8.8
- https://github.com/electron/electron/releases/tag/v40.9.0
- https://github.com/electron/electron/releases/tag/v41.2.1
- https://github.com/electron/electron/releases/tag/v42.0.0-beta.3
