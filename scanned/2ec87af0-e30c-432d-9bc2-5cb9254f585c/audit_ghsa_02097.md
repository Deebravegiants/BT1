# [M] IPC messages delivered to the wrong frame in Electron

## Summary
Severity: Medium
Advisory: GHSA-hvf8-h2qh-37m9
CVE: CVE-2020-26272
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-01-28
Source: https://github.com/advisories/GHSA-hvf8-h2qh-37m9
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <9.4.0
- npm: `electron` — affected >=10.0.0 <10.2.0
- npm: `electron` — affected >=11.0.0 <11.1.0

## Details
### Impact
IPC messages sent from the main process to a subframe in the renderer process, through `webContents.sendToFrame`, `event.reply` or when using the `remote` module, can in some cases be delivered to the wrong frame.

If your app does ANY of the following, then it is impacted by this issue:
- Uses `remote`
- Calls `webContents.sendToFrame`
- Calls `event.reply` in an IPC message handler

### Patches
This has been fixed in the following versions:

- 9.4.0
- 10.2.0
- 11.1.0
- 12.0.0-beta.9

### Workarounds
There are no workarounds for this issue.

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org).

## References
- https://github.com/electron/electron/security/advisories/GHSA-hvf8-h2qh-37m9
- https://nvd.nist.gov/vuln/detail/CVE-2020-26272
- https://github.com/electron/electron/pull/26875
- https://github.com/electron/electron/commit/07a1c2a3e5845901f7e2eda9506695be58edc73c
- https://github.com/electron/electron/commit/0bbd268eb4caf35604443df5ff196980dd49e208
- https://github.com/electron/electron/commit/36c695ce2a7e22c07fe1e30c61c00d20371daee2
- https://github.com/electron/electron/commit/429400040ecb16a21d19936658579e65a797e4cc
- https://github.com/electron/electron/commit/5c8e7e8b7f485ceafa8b271086d7b87e1de9dedd
- https://github.com/electron/electron/releases/tag/v9.4.0
- https://www.electronjs.org/releases/stable?version=9#9.4.0
