# [C] UpSnap vulnerable to Remote Code Execution via IP Field Template Injection in wake_cmd/shutdown_cmd

## Summary
Severity: Critical
Advisory: CVE-2026-49481
Aliases: GHSA-6mc7-6948-w5h4
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-49481
Type: osv

## Details
UpSnap is a wake on lan web app. Versions prior to 5.4.0 have an OS command injection vulnerability in the UpSnap’s device management functionality due to the presence of unsafe shell command template interpolation using the ip and the mac fields. User-controlled values can be inserted into the wake_cmd and shutdown_cmd templates and executed via /bin/sh -c (Linux) or cmd /C (Windows) without sanitization, resulting in an authenticated Remote Code Execution (RCE). A low-privileged user with permission to create or edit devices can execute arbitrary operating system commands on the UpSnap hosted server. Version 5.4.0 patches the issue.

## References
- https://github.com/seriousm4x/UpSnap/releases/tag/5.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49481.json
- https://github.com/seriousm4x/UpSnap/security/advisories/GHSA-6mc7-6948-w5h4
- https://nvd.nist.gov/vuln/detail/CVE-2026-49481
