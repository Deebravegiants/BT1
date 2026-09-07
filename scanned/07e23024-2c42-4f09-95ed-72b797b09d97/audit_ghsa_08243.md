# [C] Obot has an authorization bypass in /mcp-connect/{id} that allows any authenticated user to use any registered MCP server

## Summary
Severity: Critical
Advisory: GHSA-vw82-7fv8-r6gp
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-vw82-7fv8-r6gp
Type: github-advisory

## Affected
- Go: `github.com/obot-platform/obot` — affected >=0 <0.21.1

## Details
## Summary

If you have the MCP Server ID, you can connect to the MCP server even if you don't have permissions to the server.

The MCP gateway endpoint `/mcp-connect/{mcp_id}` does not enforce Access Control Rules (ACRs). Any authenticated Obot user who possesses an MCP Server ID can connect to that server through the gateway — including making tool calls — regardless of whether they are a member of any MCP Registry that grants access to the server.

In practice this means any User can fully use MCP servers that the administrator believed were restricted to specific groups.

## Severity

Reporter estimate: **Critical**.

| CVSS 3.1 metric | Value |
|---|---|
| Attack Vector | Network |
| Attack Complexity | Low |
| Privileges Required | Low (authenticated Obot user, any role ≥ Basic) |
| User Interaction | None |
| Scope | Changed (Obot authorization bypass enables access to data and operations on an upstream third-party service via Obot's stored OAuth credentials) |
| Confidentiality | High |
| Integrity | High (many MCP servers expose write tools — e.g. `updateEmployee`, `submitTimeoffRequest`, ticket creation, file writes) |
| Availability | None |
| **Vector** | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N` |
| **Score** | **9.3 / Critical** |

The upstream impact depends on which MCP servers are deployed and what scope their stored credentials hold; the bound is "everything the platform's stored OAuth/API credentials can reach."

## Affected Versions

Confirmed on `obot v0.21.0`.

## Vulnerability Details

The intended flow is that a user's authorization is checked during the OAuth process with Obot.

1. The user connects to an MCP URL through Obot.
2. During the callback, after the user logs into Obot, Obot checks that the user has access to the provided resource (the `/mcp-connect` URL in this case). Obot correctly determines the user's authorization during this flow.
3. However, another authorization check (the UI authorizer, in this case) was erroneously providing access.

## Reproduction

Tested on `obot v0.21.0`.

**Setup:**

1. Configure a multi-user MCP server connected to a sensitive backend — e.g. an HR system, ticketing system, or any service whose stored OAuth token grants broad read/write access. Note its ID.
4. Create an MCP Registry / Access Control Rule that grants this server **only** to a small group (e.g. two HR employees). Remove the `everyone` group from the relevant rule.
5. Create or identify a Basic User who is **not** a member of any registry granting access to this server.

**Exploit:**

6. Sign in as the Basic User.
7. Verify the UI does not list the server in any connector picker (it does not — that path is correctly gated).
8. Manually craft and call the gateway URL:

   ```
   POST https://<obot>/mcp-connect/<mcp_server_id>
   Authorization: <session cookie or API key>
   Content-Type: application/json

   {"jsonrpc":"2.0","id":1,"method":"tools/list"}
   ```

9. Observe a successful response listing the server's tools.
10. Issue an actual tool call:

   ```json
   {"jsonrpc":"2.0","id":2,"method":"tools/call",
    "params":{"name":"<sensitive_tool>","arguments":{...}}}
   ```

11. Observe the call succeeds, returning data scoped only by the **upstream** MCP server's OAuth credentials — not by Obot's ACRs.

The exploit works equally well via Claude Desktop / Claude Code / any MCP-aware client by configuring the gateway URL as a remote MCP endpoint with the user's API key.

## References
- https://github.com/obot-platform/obot/security/advisories/GHSA-vw82-7fv8-r6gp
- https://github.com/obot-platform/obot
- https://github.com/obot-platform/obot/releases/tag/v0.21.1
