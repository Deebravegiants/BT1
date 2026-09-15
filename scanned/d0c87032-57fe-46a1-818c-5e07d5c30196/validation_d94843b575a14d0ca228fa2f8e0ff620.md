### Title
Nil-Pointer Dereference (Precondition Failure) in `JSONRPCCodec.DecodeJSONRequest` from Unauthenticated Gateway Requests - (File: `core/services/gateway/api/jsonrpccodec.go`)

### Summary
`JSONRPCCodec.DecodeJSONRequest` unconditionally dereferences `request.Params` without checking for `nil`, even though every other JSON-RPC parsing path in the gateway explicitly treats a missing `params` field as a valid, expected state. This function is called unconditionally on every inbound request to the internet-facing gateway HTTP endpoint before any handler-level validation or authentication occurs, making it reachable by any unprivileged client.

### Finding Description
`DecodeJSONRequest` dereferences the pointer directly: [1](#0-0) 

```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)   // panics if request.Params == nil
	...
```

Every sibling parser in the same subsystem treats `Params == nil` as a normal, expected condition and returns a graceful error instead of dereferencing:
- `ValidatedMessageFromReq` explicitly checks `if req.Params == nil { return nil, errors.New("missing params attribute") }` [2](#0-1) 
- `httpTriggerHandler.validatedTriggerRequest` explicitly checks `if req.Params == nil` and returns a user-facing JSON-RPC error rather than crashing [3](#0-2) 
- The vault request processor and `vaultutils.InspectJSONRPCParams`/`TransformJSONRPCParams` also explicitly guard `params == nil` [4](#0-3) 
- Even the test suite documents this exact class of bug being fixed elsewhere: `TestGatewayVaultRequestProcessor_ProcessRequest_RejectsNilParams` and `TestVaultHandler_PreAuthValidationSkipsAuthorization`'s `"nil params"` subtest both assert graceful `InvalidVaultParamsError`/JSON-RPC error responses for requests with no `params` field [5](#0-4) [6](#0-5) 

This demonstrates the codebase's own internal understanding that "`params` omitted" is a distinct, reachable, and legitimate wire state (per JSON-RPC 2.0, `params` is optional) — but `DecodeJSONRequest` fails to make that distinction and assumes it is always present, exactly analogous to the GRPCWebToHTTP2ServerCodec bug class where the codec's internal state model was incomplete relative to what the protocol/wire format actually allowed, leading to a precondition failure.

Critically, `DecodeJSONRequest` is invoked unconditionally by the gateway's public entry point, for *every* incoming request, prior to routing, authentication, or handler dispatch: [7](#0-6) 

```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	...
```

This is invoked directly from the HTTP server's request handler for any POST to the gateway's public/user-facing port, with only an optional bearer token (`jwtToken`) extracted from the `Authorization` header — no authentication is required to reach this code: [8](#0-7) 

Since `jsonrpc2.Request.Params` is a `*json.RawMessage` and JSON-RPC 2.0 allows `params` to be entirely omitted, an unprivileged client can send a syntactically valid JSON-RPC request (e.g. `{"jsonrpc":"2.0","id":"x","method":"anything"}`) with no `params` key at all. If the upstream `jsonrpc2.DecodeRequest` (external `chainlink-common` package, not fully inspectable here) does not itself reject a nil/missing `params`, the request will reach `DecodeJSONRequest` and dereference a nil pointer, panicking.

### Impact Explanation
A nil-pointer dereference panic triggered by a single unauthenticated HTTP request to the gateway constitutes a Denial-of-Service vector on the internet-facing gateway component — the same fundamental bug class (precondition failure from incomplete internal state modeling of a malformed/edge-case request) as the referenced advisory. Depending on how panics are recovered up the call stack (net/http's `Server` typically recovers per-connection, but this must be confirmed for the actual deployed handler chain), this could crash individual request-handling goroutines repeatedly, degrade availability, or in the worst case take down the whole gateway process if no top-level recovery middleware wraps `ProcessRequest`.

### Likelihood Explanation
High. No authentication or state is required — any client capable of reaching the gateway's public HTTP endpoint can trigger this by omitting the `params` field, which is valid per JSON-RPC 2.0 and is explicitly treated as reachable/expected elsewhere in this same codebase.

### Recommendation
Add an explicit nil check in `DecodeJSONRequest` before dereferencing `request.Params`, matching the pattern already used elsewhere in the gateway (`ValidatedMessageFromReq`, `validatedTriggerRequest`, vault processors):
```go
if request.Params == nil {
    return nil, errors.New("missing params attribute")
}
```

### Proof of Concept
Send a syntactically valid JSON-RPC 2.0 request to the gateway's public HTTP endpoint with no `params` field:
```
POST /<gateway-user-endpoint> HTTP/1.1
Content-Type: application/json

{"jsonrpc":"2.0","id":"poc-1","method":"anything"}
```
This flows through `httpServer.handleRequest` → `gateway.ProcessRequest` → `JSONRPCCodec.DecodeJSONRequest`, where `*request.Params` is dereferenced on a nil pointer, panicking.

**Uncertainty**: I could not directly inspect the implementation of `jsonrpc2.DecodeRequest` in the external `chainlink-common` dependency from this index, so I cannot 100% confirm that it does not itself pre-validate/reject nil `Params` before returning. However, the codebase's own test coverage (`http_trigger_handler_test.go`, `validate_user_request_test.go`, `handler_test.go`) exercising `Params == nil` scenarios downstream strongly implies that nil/missing `params` is a state that successfully passes through `jsonrpc2.DecodeRequest` and must be handled explicitly by each consumer — which `DecodeJSONRequest` fails to do.

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

**File:** core/services/gateway/handlers/common/message_util.go (L43-45)
```go
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L149-153)
```go
func (h *httpTriggerHandler) validatedTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*jsonrpc.Request[gateway_common.HTTPTriggerRequest], error) {
	if req.Params == nil {
		h.handleUserError(ctx, "", jsonrpc.ErrInvalidRequest, "'params' field is missing. Include a valid 'params' object", callback)
		return nil, errors.New("request params is nil")
	}
```

**File:** core/capabilities/vault/vaultutils/params.go (L19-21)
```go
	if params == nil {
		return errors.New("request params must not be nil")
	}
```

**File:** core/capabilities/vault/validate_user_request_test.go (L21-37)
```go
func TestGatewayVaultRequestProcessor_ProcessRequest_RejectsNilParams(t *testing.T) {
	t.Parallel()

	validator, err := vault.NewRequestValidatorFromLimitsFactory(limits.Factory{Settings: cresettings.DefaultGetter})
	require.NoError(t, err)

	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-1",
		Method: vaulttypes.MethodSecretsCreate,
	}

	authorizer := vaultcapmocks.NewAuthorizer(t)
	processor := mustNewGatewayVaultRequestProcessor(t, validator, authorizer, false)
	err = processRequestErr(processor, t, &req)
	require.Error(t, err)
	require.True(t, vault.IsInvalidVaultParamsError(err))
}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1385-1394)
```go
	t.Run("nil params", func(t *testing.T) {
		t.Parallel()

		var wg sync.WaitGroup
		callback := common.NewCallback()

		req := jsonrpc.Request[json.RawMessage]{
			ID:     "pre-auth-nil-params",
			Method: vaulttypes.MethodSecretsCreate,
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

**File:** core/services/gateway/network/httpserver.go (L226-236)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
	duration := time.Since(startTime)
	s.hMetrics.RecordRequestDuration(r.Context(), httpStatusCode, duration)
```
