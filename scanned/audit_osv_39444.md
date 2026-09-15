# [C] Termix Vulnerable to Arbitrary Command Execution in File Manager

## Summary
Severity: Critical
Advisory: CVE-2026-45750
Aliases: GHSA-v26q-rpv5-9m72
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/CVE-2026-45750
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to version 2.3.2, the GET /ssh/file_manager/ssh/resolvePath endpoint in the Termix File Manager component unsafely processes the path parameter and embeds it into a shell command executed over the active SSH session. Because the user-controlled value is placed inside double quotes and only double quotes are escaped, shell command substitution syntax such as $(...) is still interpreted by the remote shell. Version 2.3.2 fixes the issue.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45750.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-v26q-rpv5-9m72
- https://nvd.nist.gov/vuln/detail/CVE-2026-45750
