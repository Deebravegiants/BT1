# [H] MCP Ruby SDK: Insufficient Session Binding Allows SSE Stream Hijacking via Session ID Replay

## Summary
Severity: High
Advisory: GHSA-qvqr-5cv7-wh35
CVE: CVE-2026-33946
CWE: CWE-384, CWE-639
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-qvqr-5cv7-wh35
Type: github-advisory

## Affected
- RubyGems: `mcp` — affected >=0 <0.9.2

## Details
### Summary

The Ruby SDK's [streamable_http_transport.rb](https://github.com/modelcontextprotocol/ruby-sdk/blob/main/lib/mcp/server/transports/streamable_http_transport.rb) implementation contains a session hijacking vulnerability. An attacker who obtains a valid session ID can completely hijack the victim's Server-Sent Events (SSE) stream and intercept all real-time data.

### Details
**Root Cause**
The StreamableHTTPTransport implementation stores only one SSE stream object per session ID and lacks:

- Session-to-user identity binding
- Ownership validation when establishing SSE connections
- Protection against multiple simultaneous connections to the same session

### PoC

#### Vulnerable Code

**File**: streamable_http_transport.rb - [L336-L339](https://github.com/modelcontextprotocol/ruby-sdk/blob/main/lib/mcp/server/transports/streamable_http_transport.rb#L336-L339):

```
def store_stream_for_session(session_id, stream)
  @mutex.synchronize do
    if @sessions[session_id]
      @sessions[session_id][:stream] = stream  # OVERWRITES existing stream
    else
      stream.close
    end
  end
end
```
#### Attack Scenario
**Step 1**: Legitimate Session Establishment
```
POST / (initialize) → receives session_id: "abc123"
GET / with Mcp-Session-Id: abc123 → SSE stream connected
```
Step 2: Session ID Compromise

- An attacker obtains the session ID through various means (out of scope for this analysis)

**Step 3**: Stream Hijacking

```
GET / with Mcp-Session-Id: abc123 
@sessions["abc123"][:stream] = attacker_stream `# Victim's stream is REPLACED (silently disconnected)
```

**Step 4**: Data Interception

- ALL subsequent tool responses/notifications go to the attacker
- The legitimate user receives no data and has no indication of the hijacking

#### Technical Details

The vulnerability happens:

**Client 1 connects (GET request)**

```
proc do |stream1|  # ← Rack server provides stream1 for client 1
 @sessions[session_id][:stream] = stream1  # Stored
end
```

**Client 2 connects with SAME session ID (Attack!)**
```
proc do |stream2|  # ← Rack provides stream2 for client 2
 @sessions[session_id][:stream] = stream2  # REPLACES stream1!
end
```

**Now when the server sends notifications:**

```
@sessions[session_id][:stream].write(data)  # Goes to stream2 (attacker!)
# stream1 (victim) receives nothing
```

**Comparison: Python SDK Protection**

The Python SDK prevents this vulnerability by rejecting duplicate SSE connections:

**Refer**: https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/streamable_http.py#L680-L685

```
if GET_STREAM_KEY in self._request_streams:  # pragma: no cover
            response = self._create_error_response(
                "Conflict: Only one SSE stream is allowed per session",
                HTTPStatus.CONFLICT,
            )
```

When a duplicate connection attempt is detected, the Python SDK returns an HTTP 409 Conflict error, protecting the existing connection.

**Recommended Mitigations**
**For SDK Maintainers**

- Implement User Binding: All SDKs should bind session IDs to authenticated user identities where possible. Currently only, go-sdk and csharp-sdk do user binding.
- **Ruby SDK**: Prevent Duplicate Connections: Implement checks to reject or handle multiple simultaneous connections to the same session
- **Improve Documentation**: Provide clear guidance on secure session management implementation for SDK consumers

### Steps To Reproduce:

Please find attached two python client files demonstrating the attack

**Terminal 1:**
`ruby streamable_http_server.rb`

Makes use of https://github.com/modelcontextprotocol/ruby-sdk/blob/main/examples/streamable_http_server.rb
This server has a tool call notification_tool which the clients call

**Terminal 2:**

`python3 legitimate_client_ruby_server.py`

**What happens:**

- The client connects and prints the session ID
- Press Enter to start the SSE stream
- Notifications start appearing every 3 seconds as the client makes a tool call

**Terminal 3 (while the legitimate client is running):**

`python3 attacker_client_ruby_server.py <SESSION_ID>`

Replace `<SESSION_ID>` with the ID from Terminal 2.

**What happens immediately:**

- Terminal 2 (Legitimate): Stops receiving notifications, shows disconnect message
- Terminal 3 (Attacker): Starts receiving ALL the tool call responses

### Impact
While the absence of user binding may not pose immediate risks if session IDs are not used to store sensitive data or state, the fundamental purpose of session IDs is to maintain stateful connections. If the SDK or its consumers utilize session IDs for sensitive operations without proper user binding controls, this creates a potential security vulnerability. For example: In the case of the Ruby SDK, the attacker was able to hijack the stream and receive all the tool responses belonging to the victim. The tool responses can be sensitive confidential data.

### Additional Details
#### Session Hijacking Protection in MCP Implementations
The MCP specification recommends - "MCP servers SHOULD bind session IDs to user-specific information".

#### Current Implementation Status Across SDKs

Of the 10 official MCP SDKs, only the following implementations bind session IDs to user-specific information:

1. csharp-sdk - https://github.com/modelcontextprotocol/csharp-sdk/blob/main/src/ModelContextProtocol.AspNetCore/SseHandler.cs#L93-L97
2. Go-sdk - https://github.com/modelcontextprotocol/go-sdk/blob/main/mcp/streamable.go#L281C1-L288C2

[attacker_client_ruby_server.py](https://github.com/user-attachments/files/25408485/attacker_client_ruby_server.py)
[legitimate_client_ruby_server.py](https://github.com/user-attachments/files/25408486/legitimate_client_ruby_server.py)
The remaining SDKs do not implement session-to-user binding. Most implementations only verify that a session ID exists, without validating ownership. Additionally, SDK documentation does not provide clear guidance on implementing secure session management, leaving security responsibilities unclear for SDK consumers.

## References
- https://github.com/modelcontextprotocol/ruby-sdk/security/advisories/GHSA-qvqr-5cv7-wh35
- https://nvd.nist.gov/vuln/detail/CVE-2026-33946
- https://github.com/modelcontextprotocol/ruby-sdk/commit/db40143402d65b4fb6923cec42d2d72cb89b3874
- https://hackerone.com/reports/3556146
- https://github.com/modelcontextprotocol/csharp-sdk/blob/main/src/ModelContextProtocol.AspNetCore/SseHandler.cs#L93-L97
- https://github.com/modelcontextprotocol/go-sdk/blob/main/mcp/streamable.go#L281C1-L288C2
- https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/streamable_http.py#L680-L685
- https://github.com/modelcontextprotocol/ruby-sdk
- https://github.com/modelcontextprotocol/ruby-sdk/blob/main/examples/streamable_http_server.rb
- https://github.com/modelcontextprotocol/ruby-sdk/releases/tag/v0.9.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/mcp/CVE-2026-33946.yml
