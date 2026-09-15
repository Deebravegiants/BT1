# [C] rails-mcp-server 1.4.0 through 1.6.0 OS Command Execution via execute_ruby PTY Escape

## Summary
Severity: Critical
Advisory: CVE-2026-81097
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81097
Type: osv

## Details
The execute_ruby tool is documented as a read-only Ruby sandbox and is enforced by a pattern denylist together with replacements for the process-spawning methods on Kernel. The pseudo-terminal library's spawn entry points are neither in the denylist nor replaced, so a normal tool call could reach them and start a shell, executing commands as the account running the server and outside the guarded methods. The denylist was introduced with the tool in 1.4.0 and never covered those entry points through 1.6.0. Version 1.6.1 restricts the requires the sandbox permits to a data-only list and blocks dynamic dispatch to execution entry points; 2.0.0 removes the tool.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81097.json
- https://github.com/maquina-app/rails-mcp-server/releases
- https://nvd.nist.gov/vuln/detail/CVE-2026-81097
- https://www.vulncheck.com/advisories/rails-mcp-server-1.4.0-through-1.6.0-os-command-execution-via-execute-ruby-pty-escape
- https://github.com/maquina-app/rails-mcp-server/pull/59
- https://github.com/maquina-app/rails-mcp-server
