### Title
NULL Pointer Dereference in Gateway JSON-RPC Request Decoding via Missing `params` Field - ([File: core/services/gateway/api/jsonrpccodec.go])

### Summary
The internet-facing gateway's JSON-RPC request decoder dereferences `request.Params` without checking for `nil`, allowing any unauthenticated/unprivileged HTTP client to trigger a Go nil-pointer-dereference panic by submitting a JSON-RPC request body that omits the `params` field. This is the direct code-class analog of CVE-2021-39532 (NULL pointer dereference in `slaxLexer()` reachable by attacker input causing DoS) — here the crash site is a mandatory-field-dereference bug in the message decode path of the gateway user-request pipeline instead of a lexer.

### Finding Description
`JSONRPCCodec.DecodeJSONRequest` unconditionally dereferences the `Params` pointer of an incoming JSON-RPC request before any nil check is performed: [1](#0-0) 

This function is invoked directly from the gateway's public `ProcessRequest` entry point — the function that handles every raw HTTP request coming from external/unauthenticated clients before any handler-level authentication, allowlist check, or DON-id validation occurs: [2](#0-1) 

The call sequence is:
1. `jsonrpc2.DecodeRequest` parses the raw JSON-RPC envelope (only validates the top-level structure, not that `params` is present).
2. `g.codec.DecodeJSONRequest(jsonRequest)` is called immediately afterward, on line 227, with the un-validated `jsonRequest.Params`.
3. Inside `DecodeJSONRequest`, `json.Unmarshal(*request.Params, &msg)` dereferences `request.Params` — if the incoming JSON-RPC request omits the `params` key entirely (which is legal per the JSON-RPC 2.0 spec for many methods, and there is no upstream nil-guard before this call), `request.Params` is `nil` and the dereference panics.

By contrast, other decode/handle paths in the same package explicitly guard against this exact condition, showing the codebase is aware of the hazard but missed it here: [3](#0-2) [4](#0-3) 

This confirms `DecodeJSONRequest` is missing the same "params is nil" guard that sibling code paths already implement, making it the unguarded outlier reachable earliest in the request lifecycle (before any handler-specific validation like `validatedTriggerRequest` runs).

### Impact Explanation
A panic triggered here occurs synchronously inside the HTTP request-handling call stack of the gateway's user-facing server, before any authentication or DON routing takes place — meaning it is reachable by a completely unauthenticated, unprivileged HTTP client. At minimum this aborts the specific request/connection (denial of service for that request); depending on how the gateway's HTTP server wraps handler invocation (whether a top-level `recover()` is present around `ProcessRequest`), a sustained stream of malformed requests could repeatedly panic that handling goroutine. I was not able to fully confirm within this session whether `core/services/gateway/network/httpserver.go` wraps `ProcessRequest` calls in a `recover()` (Go's `net/http` package does recover per-connection by default, but that still tears down the connection and logs a stack trace per malicious request, which is itself a low-cost repeatable DoS/noise vector against the production gateway).

### Likelihood Explanation
High. This requires nothing more than sending a JSON-RPC request whose `params` field is omitted or `null` to the gateway's public HTTP endpoint. No authentication, allowlist membership, JWT, or DON knowledge is required, since the bug is hit before any of the handler dispatch/authorization logic in `gateway.ProcessRequest` executes.

### Recommendation
Add an explicit nil-check for `request.Params` in `JSONRPCCodec.DecodeJSONRequest` (mirroring the guard already used in `ValidatedMessageFromReq` and `httpTriggerHandler.validatedTriggerRequest`) and return a structured `UserMessageParseError` instead of dereferencing the pointer. Additionally, verify/add a top-level `recover()` around the HTTP request-handling path in `core/services/gateway/network/httpserver.go` so that any similar unguarded-dereference bug in future codec/handler code cannot crash the serving goroutine.

### Proof of Concept
Send a raw JSON-RPC 2.0 request to the gateway's user HTTP endpoint with no `params` field, e.g.:
```
POST /user HTTP/1.1
Content-Type: application/jsonrpc

{"jsonrpc":"2.0","id":"1","method":"workflows.execute"}
```
`jsonrpc2.DecodeRequest` will accept this as structurally valid (it does not require `params`), producing a `Request[json.RawMessage]` with `Params == nil`. `gateway.ProcessRequest` immediately calls `g.codec.DecodeJSONRequest(jsonRequest)`, which executes `json.Unmarshal(*request.Params, &msg)` at [5](#0-4) , dereferencing a nil pointer and panicking.

### Citations

**File:** core/services/gateway/api/jsonrpccodec.go (L26-35)
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)
	if err != nil {
		return nil, err
	}
	msg.Body.MessageID = request.ID
	msg.Body.Method = request.Method
	return &msg, nil
}
```

**File:** core/services/gateway/gateway.go (L221-230)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
```

**File:** core/services/gateway/handlers/common/message_util.go (L43-45)
```go
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L150-153)
```go
	if req.Params == nil {
		h.handleUserError(ctx, "", jsonrpc.ErrInvalidRequest, "'params' field is missing. Include a valid 'params' object", callback)
		return nil, errors.New("request params is nil")
	}
```
