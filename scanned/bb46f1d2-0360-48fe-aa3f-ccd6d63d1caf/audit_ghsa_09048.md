# [H] @yoda.digital/gitlab-mcp-server's SSE transport has no authentication and wildcard CORS, exposing all 86 GitLab tools

## Summary
Severity: High
Advisory: GHSA-8jr5-6gvj-rfpf
CVE: CVE-2026-44895
CWE: CWE-306, CWE-942
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-8jr5-6gvj-rfpf
Type: github-advisory

## Affected
- npm: `@yoda.digital/gitlab-mcp-server` — affected >=0 <0.6.0

## Details
## SSE Transport Has No Authentication and Wildcard CORS, Exposing All 86 GitLab Tools Including Destructive Operations

A review of `mcp-gitlab-server` at commit `80a7b4cf3fba6b55389c0ef491a48190f7c8996a` uncovered that the SSE HTTP transport — advertised in the README and comparison table as a differentiating feature — runs with no authentication and wildcard CORS on every endpoint. The maintainers' own roadmap confirms auth is a known gap.

When `USE_SSE=true`, the HTTP server in `src/transport.ts` sets:

```typescript
res.setHeader('Access-Control-Allow-Origin', '*');
res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
```

The `httpServer.listen(port)` call at line 97 passes no host argument — Node.js defaults to `0.0.0.0`, binding on all interfaces. Two endpoints are exposed with no credential check:

- `GET /sse` — opens an SSE connection, returns a session endpoint URL
- `POST /messages?sessionId=<id>` — sends MCP messages to the server using the loaded `GITLAB_PERSONAL_ACCESS_TOKEN`

Any caller who can reach the port — LAN, cloud instance, or via the browser-tab vector the wildcard CORS enables — gets full access to all 86 tools the server exposes using the operator's GitLab PAT. That includes `delete_repository`, `delete_group`, `push_files`, `create_merge_request`, `update_repository_settings`, and any other tool the server exposes. The PAT doesn't leave the process, but every API call it backs is available to the unauthenticated caller.

The wildcard CORS makes the browser-tab vector direct: any web page the operator visits while the server is running can open an SSE connection and make tool calls via cross-origin fetch. No user interaction beyond visiting the page.

**PoC — reproduces from the documented USE_SSE=true configuration:**

```bash
# Step 1: connect SSE and capture the session endpoint
curl -N http://localhost:3000/sse &
# Output includes: event: endpoint
#                  data: /messages?sessionId=<UUID>

# Step 2: call any tool — no auth header needed
curl -X POST "http://localhost:3000/messages?sessionId=<UUID>" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_repository",
      "arguments": {"project_id": "target-org/private-repo"}
    }
  }'
# Returns repository data using the operator's GitLab PAT

# Same path works for delete_repository, push_files, etc.
```

## Root cause

The HTTP transport in `src/transport.ts` ships with no authentication layer at all and a wildcard `Access-Control-Allow-Origin: *` on every response. The structural defect is that the SSE server stands up a stateful, mutation-capable RPC endpoint that is backed by the operator's `GITLAB_PERSONAL_ACCESS_TOKEN` without any inbound credential check, then advertises itself to every cross-origin browser context via the wildcard CORS header. The `httpServer.listen(port)` call at line 97 also passes no host argument, so the bind defaults to `0.0.0.0` and exposes the auth-less surface on every interface. Auth isn't fail-opening on a missing config — there is no auth check at any code path on either `/sse` or `/messages?sessionId=...`.

## Auth boundary violated

Trust-domain boundary — untrusted cross-origin browser context (and any unauthenticated network caller) crossing into the trusted server-state-mutating GitLab API surface that the operator's PAT backs. Respected-here: nothing. The transport carries no `Authorization` check, no origin allowlist, no session-binding to the originating client, and no host restriction. Ignored-there: the SSE handler at `src/transport.ts` accepts an arbitrary `Origin` (since `Access-Control-Allow-Origin: *`), opens a session, and the matching `POST /messages?sessionId=...` proxies tool calls — including `delete_repository`, `push_files`, `update_repository_settings` — to the GitLab API using the operator's PAT. Any web page the operator visits while the server runs can drive the full 86-tool surface via cross-origin fetch.

The roadmap in `README.md` at line 190 includes `- [ ] SAML/OAuth3 authentication` — confirming the maintainers are already tracking this gap. The issue is disclosure of impact in the interim: operators who follow the README's SSE setup instructions and don't see an auth requirement in the docs may reasonably assume the transport is safe to use on a network-accessible host.

**CVSS 4.0:** `CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N` — **~6.3 (Medium)**. `AT:P` reflects the `USE_SSE=true` precondition. When that precondition is met, the effective severity for those deployments is High — full GitLab PAT access without authentication. The Medium CVSS is the aggregate across all deployments; for any operator who has activated SSE mode (which the README promotes as a feature), the finding is functionally High.

**Fix — four concrete changes:**

1. Require `MCP_GITLAB_AUTH_TOKEN` as a startup precondition when `USE_SSE=true`. If the env var is unset, the server should exit with a clear message before the HTTP server starts:

   ```typescript
   if (process.env.USE_SSE === 'true') {
     if (!process.env.MCP_GITLAB_AUTH_TOKEN) {
       console.error(
         'ERROR: MCP_GITLAB_AUTH_TOKEN must be set when USE_SSE=true. ' +
         'SSE transport without authentication exposes all GitLab tools to unauthenticated callers.'
       );
       process.exit(1);
     }
   }
   ```

   The token check in `src/transport.ts` validates it on every request:
   ```typescript
   const authToken = process.env.MCP_GITLAB_AUTH_TOKEN;
   if (authToken) {
     const provided = req.headers['authorization']?.replace(/^Bearer /, '');
     if (provided !== authToken) {
       res.writeHead(401);
       res.end(JSON.stringify({ error: 'Unauthorized' }));
       return;
     }
   }
   ```

2. Bind to `127.0.0.1` by default for the SSE transport rather than `0.0.0.0`. An explicit `MCP_GITLAB_HOST=0.0.0.0` flag with a startup banner warning can expose it to the network for operators who need that — but the safe default should be loopback-only.

3. Replace the wildcard `Access-Control-Allow-Origin: *` with a localhost-only default. When network exposure is intentional (explicit flag + auth token set), an explicit `CORS_ORIGINS` allowlist should be required.

4. The SAML/OAuth3 roadmap item is the right long-term direction. In the interim — before that ships — the three changes above are entirely in the existing codebase with no new dependencies.

---

No prior security advisories, CVEs, or public security issues exist for this package — a search of the repository issue list and npm advisory database did not yield any duplicate issues.

## References
- https://github.com/yoda-digital/mcp-gitlab-server/security/advisories/GHSA-8jr5-6gvj-rfpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44895
- https://github.com/yoda-digital/mcp-gitlab-server
