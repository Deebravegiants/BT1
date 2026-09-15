Confirmed test evidence shows the exact reachable path: `TestJsonRPCRequest_Decode_Incorrect` in `core/services/gateway/api/jsonrpccodec_test.go:38` includes the case `"missing params": '{"jsonrpc": "2.0", "id": "abc", "method": "upload"}'`, i.e. a request with **no `params` field at all**, and asserts `codec.DecodeRawRequest` returns an error rather than panicking. This means `DecodeJSONRequest` is exercised with `request.Params == nil` and the test suite expects a graceful error — but the implementation itself dereferences `*request.Params` unconditionally.

### Title
Unauthenticated Null Pointer Dereference via missing `params` field in Gateway JSON-RPC request decoding - (File: core/services/gateway/api/jsonrpccodec.go)

### Summary
`JSONRPCCodec.DecodeJSONRequest` dereferences `*request.Params` without checking for `nil`, and this function is invoked directly from `gateway.ProcessRequest`, the entry point for every unauthenticated HTTP request hitting the Chainlink Gateway.

### Finding Description
`DecodeJSONRequest` unmarshals the message body straight from the pointer without a nil guard: [1](#0-0) 

This is called unconditionally for any incoming service-routed request in `gateway.ProcessRequest`, which is the raw HTTP handler entry point invoked before authentication/handler dispatch for `serviceToMultiHandler`/`serviceNameToDonID` requests (i.e., non-legacy, DON-less requests): [2](#0-1) 

Note that `msg.Validate()` (which would catch malformed content) is only invoked in the `isLegacyRequest` branch (when `msg.Body.DonID != ""`), not in the multi-handler/service-name branch that is taken when `msg == nil || msg.Body.DonID == ""` — meaning `DecodeJSONRequest` is called on the raw `jsonRequest.Params` and if `Params` is `nil` (i.e., the client omits the `"params"` field or sends `"params": null` in an otherwise well-formed JSON-RPC 2.0 envelope), `*request.Params` dereferences a nil pointer, causing a runtime panic (Go's equivalent of a null pointer dereference crash).

The upstream `jsonrpc2.DecodeRequest` decoder used to build `jsonRequest` is out-of-repo (`chainlink-common`), so it is not verified here whether it itself defaults `Params` to a non-nil empty value or leaves it nil when absent from the JSON payload — this is the one point of uncertainty. However, the codebase's own test `TestJsonRPCRequest_Decode_Incorrect` explicitly exercises the "missing params" case through `DecodeRawRequest` (which calls `DecodeJSONRequest`) and expects an error return, confirming that `nil` `Params` is a supported/expected input state that the code fails to handle safely: [3](#0-2) 

By contrast, other handlers in the same gateway package that consume `req.Params` explicitly guard against `nil` before dereferencing, showing the codebase's established (but inconsistently applied) safe pattern: [4](#0-3) [5](#0-4) 

### Impact Explanation
A panic in an HTTP request-handling goroutine, if unrecovered, crashes the entire Gateway process (denial of service for all DON members and workflows relying on that gateway instance), matching the CVE-2017-12800 bug class (null pointer dereference causing crash from a malformed/incomplete input). This is reachable by any unauthenticated external client sending an HTTP POST to the gateway's public endpoint — no privileged credentials, keys, or node role are required. It is possible that Go's `net/http` server recovers panics per-request (standard library behavior), in which case impact would be limited to a single failed request rather than full process crash; this depends on whether the gateway's HTTP server / middleware installs a panic-recovery handler, which was not confirmed in this investigation.

### Likelihood Explanation
Very high likelihood of reachability: `ProcessRequest` is the direct entry point for all gateway HTTP requests, and sending an object without a `params` key (or `"params": null`) is a trivial, single-request attack requiring no authentication.

### Recommendation
Add a nil-check at the top of `DecodeJSONRequest` in `core/services/gateway/api/jsonrpccodec.go`, mirroring the pattern already used in `gateway_vault_request_processor.go` and `confidentialrelay/handler.go`:
```go
if request.Params == nil {
    return nil, errors.New("missing params attribute")
}
```
Additionally, verify (and add if missing) a panic-recovery middleware around the gateway's HTTP request handling so that any similar latent nil-dereference cannot bring down the whole process.

### Proof of Concept
Send the following HTTP POST body to the gateway's public JSON-RPC endpoint for a configured service (no `"don_id"` present, so the code takes the multi-handler branch that skips `msg.Validate()`):
```json
{"jsonrpc": "2.0", "id": "1", "method": "<any-registered-service-method>"}
```
i.e., omit the `params` field entirely (or set `"params": null`). This is exactly the input pattern validated by the existing unit test `TestJsonRPCRequest_Decode_Incorrect`'s `"missing params"` case, confirming `DecodeJSONRequest` is reached with `request.Params == nil`, triggering the nil dereference at `*request.Params`.

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

**File:** core/services/gateway/gateway.go (L221-238)
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
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
```

**File:** core/services/gateway/api/jsonrpccodec_test.go (L34-48)
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
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L226-237)
```go
func (p *GatewayVaultRequestProcessor) processListSecretIdentifiersRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var listReq vaultcommon.ListSecretIdentifiersRequest
	if err := json.Unmarshal(*req.Params, &listReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L98-102)
```go
func (h *handler) extractRequestLabels(req jsonrpc.Request[json.RawMessage]) requestLabels {
	var labels requestLabels
	if req.Params == nil {
		return labels
	}
```
