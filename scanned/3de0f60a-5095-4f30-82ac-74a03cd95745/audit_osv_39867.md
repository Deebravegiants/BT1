# [C] Streambert Vulnerable to Remote Code Execution (RCE) via Unvalidated Auto-Updater IPC Handler

## Summary
Severity: Critical
Advisory: CVE-2026-48046
Aliases: GHSA-vj74-r9xm-37mj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-48046
Type: osv

## Details
Streambert is a cross-platform Electron Desktop App to stream and download video content. Versions prior to 2.5.0 contain an unvalidated auto-updater URL vulnerability that allows a compromised renderer process to make the main process download and execute an arbitrary binary, resulting in remote code execution. Version 2.5.0 contains a patch.

## References
- https://github.com/truelockmc/streambert/releases/tag/2.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48046.json
- https://github.com/truelockmc/streambert/security/advisories/GHSA-vj74-r9xm-37mj
- https://nvd.nist.gov/vuln/detail/CVE-2026-48046
