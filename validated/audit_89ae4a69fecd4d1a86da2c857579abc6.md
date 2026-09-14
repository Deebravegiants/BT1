### Title
Raw internal Go error messages returned to unauthenticated clients via gateway JSON-RPC error responses - (File: core/services/gateway/gateway.go)

### Summary
The `gateway.ProcessRequest` function, which is directly reachable by any unauthenticated HTTP client hitting the gateway's user-facing port, returns raw `err.Error()` strings from internal decoding/validation failures directly in the JSON-RPC error response sent back to the caller.

### Finding Description
`ProcessRequest` in `core/services/gateway/gateway.go` is invoked from `httpServer.handleRequest` for every inbound HTTP request on the gateway's user port [1](#0-0) . On multiple failure paths, it embeds the raw Go error text into the client-visible response instead of a generic message: [2](#0-1) [3](#0-2) 

The decode path (`jsonrpc2.DecodeRequest` / `JSONRPCCodec.DecodeJSONRequest`) can surface `encoding/json` unmarshal errors verbatim, since `DecodeJSONRequest` just propagates `json.Unmarshal` errors unmodified: [4](#0-3) . Standard library JSON errors of this kind commonly include internal Go type/package information (e.g. `json: cannot unmarshal object into Go struct field Message.body of type api.MessageBody`), which is the same bug class as the referenced CVE — a REST-style endpoint leaking internal package/type names in error text due to improper error sanitization.

This is distinct from the `capabilities/v2/http_handler.go` `errorResponse` function, which explicitly redacts internal errors behind a generic `internalErrorMessage` for `jsonrpc.ErrInternal` codes [5](#0-4)  — showing the codebase is aware of this risk in some places but not in the `gateway.go` `newError` path, which has no such redaction: [6](#0-5) .

### Impact Explanation
The disclosure is limited to internal package/type names and low-detail parse error strings (e.g. `api.MessageBody`, `api.Message`), not credentials, keys, or business secrets. This matches the CVE's Low confidentiality impact — informational disclosure that could aid reconnaissance (revealing internal Go package structure) but does not by itself grant authentication bypass, key disclosure, or fund movement.

### Likelihood Explanation
Any unauthenticated client can trivially trigger this by sending a malformed JSON-RPC body (bad `params`, wrong field types, oversized ID, unknown service name) to the gateway's public HTTP endpoint — no authentication or node-membership is required, since these checks occur only after JSON decoding.

### Recommendation
In `gateway.ProcessRequest` and `newError`, replace raw `err.Error()` values for parse/decode/handler-internal failures with generic, sanitized messages (as already done for `jsonrpc.ErrInternal` in `capabilities/v2/http_handler.go`), and log the detailed error server-side only.

### Proof of Concept
Send a JSON-RPC request to the gateway user endpoint with a `params` field whose JSON type mismatches `api.Message`'s schema (e.g. a string where an object is expected). `DecodeJSONRequest` returns the raw `json.Unmarshal` error, which `ProcessRequest` embeds via `newError(jsonRequest.ID, api.UserMessageParseError, err.Error())` [7](#0-6) , exposing the internal `api.Message`/`api.MessageBody` struct/package names in the HTTP response body.

### Citations

**File:** core/services/gateway/network/httpserver.go (L233-241)
```go
	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
	duration := time.Since(startTime)
	s.hMetrics.RecordRequestDuration(r.Context(), httpStatusCode, duration)
	s.hMetrics.RecordRequestCount(r.Context(), httpStatusCode)

	w.Header().Set("Content-Type", s.config.ContentTypeHeader)
	w.WriteHeader(httpStatusCode)
	_, err = w.Write(rawResponse) //nolint:gosec // G705: response body is written with an explicit Content-Type, not rendered as HTML
```

**File:** core/services/gateway/gateway.go (L221-234)
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
```

**File:** core/services/gateway/gateway.go (L277-288)
```go
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}

	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
```

**File:** core/services/gateway/gateway.go (L297-313)
```go
func newError(id string, errCode api.ErrorCode, errMsg string) ([]byte, int) {
	response := jsonrpc2.Response[json.RawMessage]{
		Version: jsonrpc2.JsonRpcVersion,
		ID:      id,
		Error: &jsonrpc2.WireError{
			Code:    api.ToJSONRPCErrorCode(errCode),
			Message: errMsg,
			Data:    nil,
		},
	}
	rawResponse, err := json.Marshal(response)
	if err != nil {
		rawResponse = []byte("fatal error" + err.Error())
	}
	promRequest.WithLabelValues(errCode.String()).Inc()
	return rawResponse, api.ToHTTPErrorCode(errCode)
}
```

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

**File:** core/capabilities/confidentialrelay/handler.go (L1035-1038)
```go
	message := err.Error()
	if errorCode == jsonrpc.ErrInternal {
		message = internalErrorMessage
	}
```
