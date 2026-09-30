# [C] Streambert Vulnerable to Arbitrary Binary Execution via Downloader IPC Handler

## Summary
Severity: Critical
Advisory: CVE-2026-48056
Aliases: GHSA-x267-77m6-qjc9
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48056
Type: osv

## Details
Streambert is a cross-platform Electron Desktop App to stream and download video content. Versions prior to 2.5.0  improperly validate executable paths supplied to the  run-download  IPC handler, allowing a compromised renderer process to execute arbitrary local binaries with the application’s privileges. Version 2.5.0 contains a patch.

## References
- https://github.com/truelockmc/streambert/releases/tag/2.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48056.json
- https://github.com/truelockmc/streambert/security/advisories/GHSA-x267-77m6-qjc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-48056
