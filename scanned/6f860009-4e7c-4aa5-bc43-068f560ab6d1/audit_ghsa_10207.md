# [H] Electron: Use-after-free in PowerMonitor on Windows and macOS

## Summary
Severity: High
Advisory: GHSA-jjp3-mq3x-295m
CVE: CVE-2026-34770
CWE: CWE-416
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-jjp3-mq3x-295m
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <38.8.6
- npm: `electron` — affected >=39.0.0-alpha.1 <39.8.1
- npm: `electron` — affected >=40.0.0-alpha.1 <40.8.0
- npm: `electron` — affected >=41.0.0-alpha.1 <41.0.0-beta.8

## Details
### Impact
Apps that use the `powerMonitor` module may be vulnerable to a use-after-free. After the native `PowerMonitor` object is garbage-collected, the associated OS-level resources (a message window on Windows, a shutdown handler on macOS) retain dangling references. A subsequent session-change event (Windows) or system shutdown (macOS) dereferences freed memory, which may lead to a crash or memory corruption.

All apps that access `powerMonitor` events (`suspend`, `resume`, `lock-screen`, etc.) are potentially affected. The issue is not directly renderer-controllable.

### Workarounds
There are no app side workarounds, you must update to a patched version of Electron.

### Fixed Versions
* `41.0.0-beta.8`
* `40.8.0`
* `39.8.1`
* `38.8.6`

### For more information
If there are any questions or comments about this advisory, please email [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-jjp3-mq3x-295m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34770
- https://github.com/electron/electron
