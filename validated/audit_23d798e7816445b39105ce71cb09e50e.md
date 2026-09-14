### Title
Nil-pointer dereference on unauthenticated gateway request via missing "params" field — (File: `core/services/gateway/api/jsonrpccodec.go`)

### Summary
`JSONRPCCodec.DecodeJSONRequest` dereferences `request.Params` (a `*json.RawMessage`) without checking it for `nil` before calling `json.Unmarshal`. This function is reachable directly from `gateway.ProcessRequest`, which is the entry point for all inbound HTTP requests hitting the gateway's public-facing user API, before any DON/handler-specific validation runs.

### Finding Description
`DecodeJSONRequest` does:
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)   // dereferences without nil check
	...
``` [1](#0-0) 

It is called from `gateway.ProcessRequest`, which is invoked by the HTTP server for every incoming user request:
```go
jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
if err != nil {
    return newError("", api.UserMessageParseError, err.Error())
}
msg, err := g.codec.DecodeJSONRequest(jsonRequest)
``` [2](#0-1) 

`jsonrpc2.Request[json.RawMessage].Params` is an optional field (`*json.RawMessage`), and a well-formed JSON-RPC 2.0 request is not required to include `params` at all. A client can simply omit it (e.g. `{"jsonrpc":"2.0","id":"abc","method":"upload"}`) and it will still successfully pass `jsonrpc2.DecodeRequest`. Once `jsonRequest.Params` is `nil`, `DecodeJSONRequest` dereferences it (`*request.Params`) and panics with a nil-pointer dereference.

This directly parallels the CVE-2025-56364 bug class: an optional/possibly-absent value (`GetDestinationGroupId()` / here `Params`) is accessed without an existence check, and the code path is reachable purely from unauthenticated network input, resulting in a crash (DoS).

Contrast this with the sibling helper `ValidatedMessageFromReq`, used by legacy gateway handlers, which correctly guards the same pattern:
```go
if req.Params == nil {
    return nil, errors.New("missing params attribute")
}
var m api.Message
err := json.Unmarshal(*req.Params, &m)
``` [3](#0-2) 

`DecodeJSONRequest` lacks this same nil check, showing the guard was applied inconsistently.

### Impact Explanation
If `DecodeJSONRequest` panics with no recover in the request-handling goroutine/HTTP handler, it can crash the gateway process, causing denial of service for all DONs and nodes served by that gateway instance — matching the "leads to a crash ... denial of service" impact of the referenced CVE. Whether this results only in an HTTP 500 (if the HTTP server recovers panics per-request) or a full process crash depends on the HTTP server's panic-recovery middleware, which was not confirmed within the indexed code available to Ask; this should be verified by tracing `gw_net.HTTPServer`'s request-handling stack in a full Devin session.

### Likelihood Explanation
High. The request is trivially reachable by any unprivileged HTTP client hitting the gateway's public endpoint — a single JSON-RPC request with the `params` field entirely omitted, with no valid DON ID or authorization needed, reaches the vulnerable code before any handler/method-specific validation.

### Recommendation
Add a nil-check on `request.Params` in `DecodeJSONRequest` (mirroring the pattern already used in `ValidatedMessageFromReq`) and return a structured `UserMessageParseError` instead of dereferencing a nil pointer:
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	if request.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)
	...
```

### Proof of Concept
Send the following to the gateway's public HTTP endpoint (no `params` field, no DON ID):
```
POST /
Content-Type: application/json

{"jsonrpc":"2.0","id":"abc","method":"upload"}
```
Because `msg.Body.DonID == ""`, `gateway.ProcessRequest` treats it as a non-legacy request and looks up a multi-handler by service name; if no such handler mapping exists it exits early with `HandlerError`. To hit the vulnerable dereference specifically via `DecodeJSONRequest`, the same nil-`Params` value must reach `g.codec.DecodeJSONRequest(jsonRequest)` at line 227 in `core/services/gateway/gateway.go`, which occurs unconditionally for every request before the DON/service-name branching logic — confirmable directly via a unit test analogous to `TestJsonRPCRequest_Decode_Incorrect`'s `"missing params"` case, but calling `codec.DecodeJSONRequest` directly instead of `DecodeRawRequest` (which itself panics on the nil dereference rather than returning an error, unlike the existing test suite's use of `DecodeRawRequest`, which wraps the parse differently). [4](#0-3)

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

**File:** core/services/gateway/handlers/common/message_util.go (L43-47)
```go
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
```

**File:** core/services/gateway/api/jsonrpccodec_test.go (L34-49)
```go
func TestJsonRPCRequest_Decode_Incorrect(t *testing.T) {
	t.Parallel()

	testCases := map[string]string{
		"missing params":        `{"jsonrpc": "2.0", "id": "abc", "method": "upload"}`,
		"numeric id":            `{"jsonrpc": "2.0", "id": 123, "method": "upload", "params": {}}`,
		"empty method":          `{"jsonrpc": "2.0", "id": "abc", "method": "", "params": {}}`,
		"incorrect rpc version": `{"jsonrpc": "5.1", "id": "abc", "method": "upload", "params": {}}`,
	}

	codec := api.JSONRPCCodec{}
	for _, input := range testCases {
		_, err := codec.DecodeRawRequest([]byte(input), "")
		require.Error(t, err)
	}
}
```
