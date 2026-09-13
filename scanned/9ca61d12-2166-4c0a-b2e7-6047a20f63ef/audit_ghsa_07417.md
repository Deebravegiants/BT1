# [H] GitHub MCP Server has Nil Pointer Dereference DoS in completion/complete Handler

## Summary
Severity: High
Advisory: GHSA-w4q6-qw23-4rg7
CVE: CVE-2026-47427
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-w4q6-qw23-4rg7
Type: github-advisory

## Affected
- Go: `github.com/github/github-mcp-server` — affected >=0 <1.1.0

## Details
### Summary

A nil pointer dereference vulnerability in the GitHub MCP Server causes it to crash when receiving a malformed `completion/complete` request with missing or empty parameters. This allows any unauthenticated client to cause a complete denial of service.

### Details

The `CompletionsHandler` function in `pkg/github/server.go:198` accesses `params.Ref` without checking if it's nil first. When a client sends a `completion/complete` request with a missing `ref` field, the handler dereferences nil and the Go runtime panics.

The crash occurs before any authentication or token validation, so even requests with fake tokens can trigger it.

### PoC

After completing the MCP initialization handshake, send either:

**Empty params:**

    {"jsonrpc":"2.0","id":2,"method":"completion/complete","params":{}}

**Missing ref field:**

    {"jsonrpc":"2.0","id":2,"method":"completion/complete","params":{"argument":{"name":"x","value":"y"}}}

**Result:**

    panic: runtime error: invalid memory address or nil pointer dereference
    goroutine 42 [running]:
    github.com/github/github-mcp-server/pkg/github.NewMCPServer.CompletionsHandler.func1(...)
        pkg/github/server.go:198 +0x24

### Impact

Any unauthenticated client that can send JSON-RPC messages to the server can crash it immediately. This is a complete denial of service - the panic is unrecoverable and kills the process.

Automated fuzzing with mcpsec found 108 crashes out of 925 test cases (11.7% crash rate).

### Timeline

- **Feb 21, 2026** - Initial report sent to opensource-security@github.com
- **Mar 03, 2026** - Follow-up email sent, no response
- **Mar 21, 2026** - Re-verified on v0.33.0, sent detailed report with PoC, no response
- **Apr 06, 2026** - GHSA filed after 44 days without acknowledgment

### Suggested Fix

    func (s *Server) CompletionsHandler(ctx context.Context, params *mcp.CompleteParams) (*mcp.CompleteResult, error) {
        if params == nil || params.Ref == nil {
            return nil, fmt.Errorf("invalid request: missing ref parameter")
        }
        // ... rest of handler
    }

## References
- https://github.com/github/github-mcp-server/security/advisories/GHSA-w4q6-qw23-4rg7
- https://github.com/github/github-mcp-server/pull/2502
- https://github.com/github/github-mcp-server/commit/c88d2ecdd3bb07f7bdd75296e3ee676febf14f58
- https://github.com/github/github-mcp-server
- https://github.com/github/github-mcp-server/releases/tag/v1.1.0
