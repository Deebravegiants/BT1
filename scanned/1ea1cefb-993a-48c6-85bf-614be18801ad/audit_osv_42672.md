# [C] radare2-mcp <=1.6.0 OS Command Injection via Shell Metacharacter Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-6942
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-6942
Type: osv

## Details
radare2-mcp version 1.6.0 and earlier contains an os command injection vulnerability that allows remote attackers to execute arbitrary commands by bypassing the command filter through shell metacharacters in user-controlled input passed to r2_cmd_str(). Attackers can inject shell metacharacters through the jsonrpc interface parameters to achieve remote code execution on the host running radare2-mcp without requiring authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6942.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6942
- https://www.vulncheck.com/advisories/radare2-mcp-os-command-injection-via-shell-metacharacter-bypass
- https://github.com/radareorg/radare2-mcp/issues/45
- https://github.com/radareorg/radare2-mcp/commit/482cde6500009112a8bc0b3fa8d2ef6180581ec0
