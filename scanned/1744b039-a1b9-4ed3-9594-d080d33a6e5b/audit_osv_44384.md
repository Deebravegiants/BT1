# [C] UI-TARS-desktop @agent-infra MCP Servers Bind Every Interface Without Authentication, Exposing Arbitrary Command Execution

## Summary
Severity: Critical
Advisory: CVE-2026-81735
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81735
Type: osv

## Details
startServer.ts in the mcp-http-server package of UI-TARS-desktop defaulted its listen address to '::' when no host was given, so startSseAndStreamableHttpMcpServer bound the Streamable HTTP and SSE MCP transports to every interface, and its authentication middleware was optional: middlewares are applied only when a caller supplies them. The @agent-infra/mcp-server-commands and @agent-infra/mcp-server-filesystem entry points call startSseAndStreamableHttpMcpServer with a host and port alone and pass no middleware, so neither server required a credential. The commands server exposes a run_command tool that hands its caller-supplied command string to promisify(child_process.exec), so any unauthenticated client able to reach the port could run arbitrary commands as the user running the server, and the filesystem server exposed its file read and write tools on the same terms. The listen default became 127.0.0.1 in commit c2ad42e3eb9b27830db41a3e6f51ca7179d9b168; the package version stayed at 1.2.4 across that change, so the boundary is the commit rather than a release.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81735.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81735
- https://www.vulncheck.com/advisories/ui-tars-desktop-agent-infra-mcp-servers-bind-every-interface-without-authentication-exposing-arbitrary-command-execution
- https://github.com/bytedance/UI-TARS-desktop/commit/c2ad42e3eb9b27830db41a3e6f51ca7179d9b168
- https://github.com/bytedance/UI-TARS-desktop/pull/1918
- https://github.com/bytedance/UI-TARS-desktop
- https://github.com/bytedance/UI-TARS-desktop/blob/e9f3387288da4af2ad99972da2ac916cdabce093/packages/agent-infra/mcp-http-server/src/startServer.ts#L263
