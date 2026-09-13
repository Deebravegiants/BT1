# [H] Streambert: Arbitrary File Execution via VLC/mpv Launcher Fallback

## Summary
Severity: High
Advisory: CVE-2026-52876
Aliases: GHSA-85vf-2qwc-qpm4
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-52876
Type: osv

## Details
Streambert is a cross-platform Electron Desktop App to stream and download video content. Prior to version 2.6.0, the open-path-at-time IPC handler in src/ipc/player.js accepts a renderer-controlled filePath without validating its type or location. If the mpv or VLC launch attempts are skipped or fail, the handler passes filePath to Electron's shell.openPath. A compromised renderer can provide the path of a local executable, script, shortcut, or other file with an executing default handler, causing the operating system to launch it with the privileges of the StreamBERT process and enabling escape from the renderer sandbox. This issue is fixed in version 2.6.0.

## References
- https://github.com/truelockmc/streambert/releases/tag/2.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52876.json
- https://github.com/truelockmc/streambert/security/advisories/GHSA-85vf-2qwc-qpm4
- https://nvd.nist.gov/vuln/detail/CVE-2026-52876
- https://github.com/truelockmc/streambert/commit/43566ed031183b046675761c9813c5379b619269
- https://github.com/truelockmc/streambert/pull/149
