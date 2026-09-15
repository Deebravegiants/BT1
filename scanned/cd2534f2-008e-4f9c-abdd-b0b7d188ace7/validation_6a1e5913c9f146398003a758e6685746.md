### Title
Unvalidated `nil` JSON-RPC `params` causes NULL pointer dereference in Gateway's internet-facing request handler - (File: core/services/gateway/api/jsonrpccodec.go)

### Summary
The FFmpeg CVE root cause is a missing check for a nil/failed result before dereferencing it during header parsing, causing a crash on attacker-controlled input. The Chainlink Gateway has an analogous pattern: `(*JSONRPCCodec) DecodeJSONRequest` unconditionally dereferences `request.Params` without checking for `nil`, and this function sits directly in the path of unauthenticated, internet-facing client requests.

### Finding Description
`DecodeJSONRequest` unmarshals the request body by dereferencing `request.Params` unconditionally: [1](#0-0) 

`Params` is typed as `*json.RawMessage` (a pointer), and standard JSON-RPC 2.0 permits omitting the `params` field entirely for requests that don't need it. If a client sends a JSON-RPC request without a `params` field, `jsonrpc2.DecodeRequest` will produce a `Request` with `Params == nil`, and `*request.Params` dereferences a nil pointer, panicking.

This function is called directly from the gateway's externally-reachable HTTP entry point, `gateway.ProcessRequest`, which is explicitly documented as "Called by the server": [2](#0-1) 

Unlike the legacy message path (`common.ValidatedMessageFromReq`), which explicitly checks `req.Params == nil` before use: [3](#0-2) 

the new JSON-RPC codec path used by `ProcessRequest` for non-legacy (DON-ID-less) requests has no equivalent nil check before calling `g.codec.DecodeJSONRequest(jsonRequest)`: [4](#0-3) 

This is precisely the FFmpeg bug-class analog: a parsing/decoding routine that can be called with input state that was never validated to be non-nil (missing check for failure/absence akin to `init_get_bits8()` returning failure), and the caller trusts the pointer is valid and dereferences it, causing a NULL pointer dereference.

### Impact Explanation
A panic reachable from unauthenticated network input in the gateway's HTTP handler goroutine can crash the serving goroutine (and, depending on how panics are recovered upstream in the HTTP server framework, potentially the whole gateway process if not recovered), resulting in denial of service against the gateway node — analogous in impact to the CVSS 6.5 (availability-impact-only) rating of CVE-2018-13303.

### Likelihood Explanation
Likelihood is high if reachable: it requires only a single unauthenticated HTTP POST with a syntactically valid JSON-RPC 2.0 envelope (`{"jsonrpc":"2.0","id":"x","method":"someService"}`) that omits the `params` key, targeting a `serviceName` that maps to `serviceToMultiHandler` or `serviceNameToDonID` (non-legacy request path) so that the flow reaches `g.codec.DecodeJSONRequest`. I could not fully confirm from the available index whether Go's HTTP server (`net/http`) recovers panics per-request by default without additional middleware in this codebase (`net/http`'s `Server` recovers panics in `conn.serve` and logs them, closing only that connection, not crashing the whole process) — so the ultimate blast radius may be limited to the one connection rather than full DoS, unlike the FFmpeg CLI process crash. This should be verified with a full read of `gw_net.NewHTTPServer` and its request dispatch code, which the index does not fully surface.

### Recommendation
Add an explicit nil check on `request.Params` in `DecodeJSONRequest` (and any other codec/decoder that dereferences `*Request.Params` or `*Response.Result`) before dereferencing, returning a structured JSON-RPC parse/invalid-params error instead of panicking, mirroring the existing check in `common.ValidatedMessageFromReq`.

### Proof of Concept
Send to the gateway's user-facing HTTP port:
```
POST /
Content-Type: application/json

{"jsonrpc":"2.0","id":"1","method":"<a configured serviceName>"}
```
With no `"params"` field, `jsonRequest.Params` is `nil`; `g.codec.DecodeJSONRequest(jsonRequest)` calls `json.Unmarshal(*request.Params, &msg)`, dereferencing a nil `*json.RawMessage` and panicking.

**Note on confidence**: I could not verify from the indexed code whether an upstream HTTP middleware/recover wraps this call path to contain the panic to a single request versus crashing the server process; this affects whether the impact is "process DoS" vs. "single-request failure." A Devin session with full repository access would be needed to trace `gw_net.NewHTTPServer`'s request-serving code to confirm panic-recovery behavior and confirm exploitability end-to-end.

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

**File:** core/services/gateway/gateway.go (L220-238)
```go
// Called by the server
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
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
```

**File:** core/services/gateway/handlers/common/message_util.go (L36-45)
```go
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
```
