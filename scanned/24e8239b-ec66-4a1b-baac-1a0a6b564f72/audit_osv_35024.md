# [C] Fireshare Public Uploads feature is vulnerable to OS Command Injection (RCE)

## Summary
Severity: Critical
Advisory: CVE-2025-67728
Aliases: GHSA-c4f5-g622-q72m
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-12
Source: https://osv.dev/vulnerability/CVE-2025-67728
Type: osv

## Details
Fireshare facilitates self-hosted media and link sharing. Versions 1.2.30 and below allow an authenticated user, or unauthenticated user if the Public Uploads setting is enabled, to craft a malicious filename when uploading a video file. The malicious filename is then concatenated directly into a shell command, which can be used for uploading files to arbitrary directories via path traversal, or executing system commands for Remote Code Execution (RCE). This issue is fixed in version 1.3.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67728.json
- https://github.com/ShaneIsrael/fireshare/security/advisories/GHSA-c4f5-g622-q72m
- https://nvd.nist.gov/vuln/detail/CVE-2025-67728
- https://github.com/ShaneIsrael/fireshare/commit/157386c85f6683f89192dae52115069b435b6d34
