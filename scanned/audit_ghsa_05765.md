# [M] Electron: DevTools embedder handler executes arbitrary files via shell open

## Summary
Severity: Medium
Advisory: GHSA-f2r8-jv7c-xqmp
CVE: CVE-2026-70611
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-f2r8-jv7c-xqmp
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.9
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.2
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.1
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.3

## Details
### Impact
The DevTools "reveal in file manager" action could launch the target file rather than reveal it. An attacker with a separate means of running script inside the DevTools frontend (such as a malicious DevTools extension) could use this to execute native code outside the sandbox.

Apps are only affected if DevTools is opened for windows exposed to untrusted content or untrusted DevTools extensions. Apps that do not open DevTools in that context are not affected.

### Workarounds
Do not open DevTools for windows that load untrusted content, and do not load untrusted DevTools extensions.

### Fixed Versions
* `42.0.0-beta.3`
* `41.2.1`
* `40.9.2`
* `39.8.9`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-f2r8-jv7c-xqmp
- https://github.com/electron/electron/pull/50937
- https://github.com/electron/electron/pull/50938
- https://github.com/electron/electron/pull/51114
- https://github.com/electron/electron/pull/51115
- https://github.com/electron/electron/commit/10fb5b39c5287f70c4bbcab4c24197f3871ec322
- https://github.com/electron/electron/commit/27bf1cae9274d5025684c7268496f435b7e06b44
- https://github.com/electron/electron/commit/7a1eb7e5585991b3726cedb890a6244f327f43de
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v39.8.9
- https://github.com/electron/electron/releases/tag/v40.9.2
- https://github.com/electron/electron/releases/tag/v41.2.1
- https://github.com/electron/electron/releases/tag/v42.0.0-beta.3
