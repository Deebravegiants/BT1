# [H] Streambert : Insecure Protocol Execution in open-external IPC Handler

## Summary
Severity: High
Advisory: CVE-2026-52877
Aliases: GHSA-j2vw-gg3g-wwqr
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-52877
Type: osv

## Details
Streambert is a cross-platform Electron Desktop App to stream and download video content. Prior to version 2.6.0, the open-external IPC handler in src/ipc/downloads.js passes a renderer-supplied url directly to Electron's shell.openExternal without validating its protocol. A compromised renderer can submit file: URIs or operating-system-specific custom schemes, causing the host to open local files, access remote resources through registered handlers, or launch scripts and applications supported by those handlers. This issue is fixed in version 2.6.0.

## References
- https://github.com/truelockmc/streambert/releases/tag/2.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52877.json
- https://github.com/truelockmc/streambert/security/advisories/GHSA-j2vw-gg3g-wwqr
- https://nvd.nist.gov/vuln/detail/CVE-2026-52877
- https://github.com/truelockmc/streambert/commit/8fd7eb1d358d1d69e57e51ddfa71b066b44ff616
