# [C] ToolUniverse through 1.2.6 Unauthenticated Remote Code Execution via python_code_executor Sandbox Escape

## Summary
Severity: Critical
Advisory: CVE-2026-81096
Aliases: GHSA-pxwq-22vf-87fm
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81096
Type: osv

## Details
ToolUniverse ran caller-supplied Python inside a sandbox that could be escaped, on a server that required no authentication. The executor behind the python_code_executor tool, in python_executor_tool.py, inspected the submitted source for a denied list of attribute names and calls but left the attribute-lookup builtins available and did not stop a dunder attribute reached through a string lookup or through a module already permitted, so a caller could walk from a literal's class to its base and enumerate subclasses to obtain a reference to the process and subprocess modules. A per-call argument also let the caller widen the import allow-list before the inspection ran. The HTTP and MCP servers in http_api_server.py and smcp_server.py bound to every interface with debugging enabled and no authentication, so any caller able to reach the port executed code as the server process. Version 1.3.0 adds bearer-token authentication, defaults the bind address to loopback, and hardens the attribute checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81096.json
- https://github.com/mims-harvard/ToolUniverse/security/advisories/GHSA-pxwq-22vf-87fm
- https://nvd.nist.gov/vuln/detail/CVE-2026-81096
- https://www.vulncheck.com/advisories/tooluniverse-through-1.2.6-unauthenticated-remote-code-execution-via-python-code-executor-sandbox-escape
- https://github.com/mims-harvard/ToolUniverse/pull/251
- https://github.com/mims-harvard/ToolUniverse
