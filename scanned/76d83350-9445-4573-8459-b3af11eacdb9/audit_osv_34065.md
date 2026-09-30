# [H] Roo Code Lacks Line Break Validation in its Command Execution Tool

## Summary
Severity: High
Advisory: CVE-2025-54377
Aliases: GHSA-p278-52x9-cffx
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-23
Source: https://osv.dev/vulnerability/CVE-2025-54377
Type: osv

## Details
Roo Code is an AI-powered autonomous coding agent that lives in users' editors. In versions 3.23.18 and below, RooCode does not validate line breaks (\n) in its command input, allowing potential bypass of the allow-list mechanism. The project appears to lack parsing or validation logic to prevent multi-line command injection. When commands are evaluated for execution, only the first line or token may be considered, enabling attackers to smuggle additional commands in subsequent lines. This is fixed in version 3.23.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54377.json
- https://github.com/RooCodeInc/Roo-Code/security/advisories/GHSA-p278-52x9-cffx
- https://nvd.nist.gov/vuln/detail/CVE-2025-54377
- https://github.com/RooCodeInc/Roo-Code/commit/9d434c2db9b20eb5c78b698cb2b0037cd2074534
