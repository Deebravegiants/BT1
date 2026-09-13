# [C] LocalSend path traversal vulnerability in the file upload endpoint allows nearby devices to execute arbitrary commands

## Summary
Severity: Critical
Advisory: CVE-2025-27142
Aliases: GHSA-f7jp-p6j4-3522
CVSS: 9.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-02-25
Source: https://osv.dev/vulnerability/CVE-2025-27142
Type: osv

## Details
LocalSend is a free, open-source app that allows users to securely share files and messages with nearby devices over their local network without needing an internet connection. Prior to version 1.17.0, due to the missing sanitization of the path in the `POST /api/localsend/v2/prepare-upload` and the `POST /api/localsend/v2/upload` endpoint, a malicious file transfer request can write files to the arbitrary location on the system, resulting in the remote command execution. A malicious file transfer request sent by nearby devices can write files into an arbitrary directory. This usually allows command execution via the startup folder on Windows or Bash-related files on Linux. If the user enables the `Quick Save` feature, it will silently write files without explicit user interaction. Version 1.17.0 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27142.json
- https://github.com/localsend/localsend/security/advisories/GHSA-f7jp-p6j4-3522
- https://nvd.nist.gov/vuln/detail/CVE-2025-27142
- https://github.com/localsend/localsend/commit/e8635204ec782ded45bc7d698deb60f3c4105687
