# [H] MCP Ruby SDK: Ruby SSE Session Poisoning

## Summary
Severity: High
Advisory: GHSA-5p9g-j988-pcwv
CVE: CVE-2026-67431
CWE: CWE-284
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-5p9g-j988-pcwv
Type: github-advisory

## Affected
- RubyGems: `mcp` — affected >=0 <0.23.0

## Details
### Summary
**Vulnerability**: Missing Session Ownership Validation in the Ruby MCP SDK's Streamable and SSE HTTP transport implementation. Any attacker with a stolen session ID can execute tools with the victim's session. This is a silent attack - the victim's session is compromised and being used for unauthorized actions, but it is hard to know for the victim

### Details
https://github.com/modelcontextprotocol/ruby-sdk/blob/main/lib/mcp/server/transports/streamable_http_transport.rb#L260-L278

**Victim** starts a legitimate MCP session and receives session ID abc-123
**Attacker** obtains the session ID (various means - network sniffing, logs, etc. out of scope for this analysis)
**Attacker** sends POST to /messages/abc-123 with a tool call
**Server** accepts the request (no ownership validation!)
**Server** executes the tool and sends response to victim's SSE stream
**Victim** receives attacker's response, thinking it's legitimate

### PoC
[attacker_client.py](https://github.com/user-attachments/files/26044817/attacker_client.py)
[legitimate_client.py](https://github.com/user-attachments/files/26044818/legitimate_client.py)

**Prerequisites**

1. Python 3.8+
2. Install dependencies: `requests`

**Running the Demo**

1. **Terminal 1:** Start the Ruby MCP Server

`ruby streamable_http_server.rb`

Makes use of https://github.com/modelcontextprotocol/ruby-sdk/blob/main/examples/streamable_http_server.rb
This server has a tool call notification_tool which the clients call

2. **Terminal 2:**  Start Victim Client

`python3 legitimate_client.py`

3.  **Terminal 3** - Attacker Client:

Copy the session ID from Terminal 1 and run:

```bash
python3 attacker_client.py abc-123-def-456
```
4. **Back to Terminal 2** - Victim sees the injected response:

### Impact

- **Integrity:** HIGH - Attacker can execute unauthorized tools and modify state
- **Availability:** LOW - Attacker can disrupt victim's session with injected responses

### Additional Details
Session Hijacking Protection in MCP Implementations

The MCP specification recommends - "[MCP servers SHOULD bind session IDs to user-specific information](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices#mitigation-4)".

#### User Binding - Comparison other SDKs
**csharp-sdk**

- https://github.com/modelcontextprotocol/csharp-sdk/blob/main/src/ModelContextProtocol.AspNetCore/SseHandler.cs#L36
- https://github.com/modelcontextprotocol/csharp-sdk/blob/main/src/ModelContextProtocol.AspNetCore/SseHandler.cs#L95-L98

**Go-sdk**

- https://github.com/modelcontextprotocol/go-sdk/blob/main/mcp/streamable.go#L66
- https://github.com/modelcontextprotocol/go-sdk/blob/main/mcp/streamable.go#L316-L320

#### Comparison with the Stream Replacement vulnerability 

**Stream Replacement**
https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-qvqr-5cv7-wh35

- **Target**: SSE stream connection
- **Attack Vector**: GET /mcp
- **What happens to Victim**: The connection is disconnected and doesn't receive reponses 

**Session Poisoning**

- **Target**: Tool execution
- **Attack Vector**: POST /mcp
- **What happens to Victim**: The connection stays connected and receives responses of tool calls by attacker

## References
- https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-5p9g-j988-pcwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-67431
- https://github.com/modelcontextprotocol/ruby-sdk/commit/35466605319a34e4c7808712ae9bb1ca1afb2356
- https://github.com/modelcontextprotocol/ruby-sdk
- https://github.com/modelcontextprotocol/ruby-sdk/releases/tag/v0.23.0
