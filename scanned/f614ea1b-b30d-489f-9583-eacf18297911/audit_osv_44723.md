# [M] ogx 1.3.1 Server-Side Request Forgery via MCP tool server_url

## Summary
Severity: Medium
Advisory: CVE-2026-85666
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85666
Type: osv

## Details
OGX (formerly Llama Stack, affected at commit fbe8e0f) contains an unauthenticated server-side request forgery vulnerability in the OpenAI-compatible POST /v1/responses endpoint. MCP tool definitions accept a server_url parameter (along with headers and authorization values) that is fetched server-side without destination validation; the existing validate_url_not_private() guard used for other URL inputs is not applied to server_url. On the default starter configuration, which runs without authentication, a remote unauthenticated attacker can cause the server to open connections to arbitrary internal addresses (including cloud metadata endpoints such as http://169.254.169.254/) and forward attacker-supplied headers and bearer tokens to those destinations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85666.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85666
- https://www.vulncheck.com/advisories/ogx-1.3.1-server-side-request-forgery-via-mcp-tool-server-url
- https://github.com/ogx-ai/ogx/issues/6287
- https://github.com/ogx-ai/ogx
- https://github.com/ogx-ai/ogx/blob/v1.3.1/src/ogx/providers/utils/tools/mcp.py
