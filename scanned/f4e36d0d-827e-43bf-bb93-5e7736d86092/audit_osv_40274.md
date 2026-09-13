# [H] Streambert: Local File Exfiltration and Overwrite via Subtitle file: Protocol

## Summary
Severity: High
Advisory: CVE-2026-52872
Aliases: GHSA-v74h-2468-rxhh
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-52872
Type: osv

## Details
Streambert is a cross-platform Electron Desktop App to stream and download video content. Prior to 2.5.0, the downloadSubtitleFile utility in src/ipc/downloads.js, reached through the run-download IPC channel, accepts a renderer-supplied subtitle url using the file: URI scheme and passes its decoded pathname to fs.copyFileSync. The renderer also controls downloadPath, which determines the destination path. A compromised renderer can therefore copy any file readable by the StreamBERT process into an attacker-chosen writable location, exposing sensitive local data, and can overwrite existing writable files. This vulnerability is fixed in 2.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52872.json
- https://github.com/truelockmc/streambert/security/advisories/GHSA-v74h-2468-rxhh
- https://nvd.nist.gov/vuln/detail/CVE-2026-52872
