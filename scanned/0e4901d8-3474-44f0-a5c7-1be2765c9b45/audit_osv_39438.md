# [C] Termix has an OS Command Injection in File Manager resolvePath endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-45744
Aliases: GHSA-37f4-wq95-pg33
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-45744
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to version 2.3.2, the GET /ssh/file_manager/ssh/resolvePath endpoint in Termix is vulnerable to OS command injection. The endpoint uses double-quote escaping for shell command construction, which does not prevent $(...) and backtick command substitution. Any authenticated user with an active File Manager SSH session can execute arbitrary commands on the connected remote host. Version 2.3.2 patches the issue.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45744.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-37f4-wq95-pg33
- https://nvd.nist.gov/vuln/detail/CVE-2026-45744
