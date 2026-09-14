## Finding

### Title
Gateway `ProcessRequest` forwards raw internal handler error text to unauthenticated HTTP clients - (File: `core/services/gateway/gateway.go`)

### Summary
Chainlink's Gateway service exposes a public, internet-facing HTTP endpoint (`httpServer` on the "user port") that unauthenticated/unprivileged external clients hit directly. When an internal handler call fails, `gateway.ProcessRequest` wraps the raw Go `error.Error()` string into the wire-level JSON-RPC error response with no redaction, unlike other handlers in the same codebase that explicitly gate this behavior.

### Finding Description
In `core/services/gateway/gateway.go`, `ProcessRequest` dispatches to a handler and, on failure, returns the internal error text verbatim to the caller: [1](#0-0) 

This flows into `newError`, which marshals it straight into the JSON-RPC wire error `Message` field sent back over HTTP: [2](#0-1) 

The HTTP transport that calls `ProcessRequest` sits directly on the network boundary and accepts any request (with only an optional bearer token extracted, not enforced at this layer): [3](#0-2) 

By contrast, other handlers in the same package deliberately avoid this pattern — e.g. `confidentialrelay/handler.go`'s `errorResponse` substitutes a generic `internalErrorMessage` for internal errors instead of the raw error string: [4](#0-3) 

and `vault/handler.go`'s `errorResponse` explicitly comments "Intentionally hide the error from the user" for encoding errors: [5](#0-4) 

`gateway.go`'s top-level `ProcessRequest`/`newError` path has no equivalent gating for `api.HandlerError` — whatever `err.Error()` the underlying `HandleJSONRPCUserMessage`/`HandleLegacyUserMessage` call produces (which can include wrapped internal context such as datastore/config errors, DON routing internals, or downstream dependency error text) is propagated to the wire response unfiltered.

### Impact Explanation
This mirrors the Flight `Engine::_error()` bug class: an unauthenticated/unprivileged actor sending a malformed or edge-case request to the gateway's public HTTP port can trigger internal handler failures whose raw error text — potentially containing internal state, configuration values, or downstream error context not intended for external disclosure — is returned directly in the HTTP response body. This is a genuine CWE-209-style information disclosure primitive on an internet-facing entry point, though severity is lower than the Flight PoC since Go errors here are less likely to contain absolute filesystem paths/stack traces by default.

### Likelihood Explanation
Reachable by any unauthenticated client capable of sending a request to the gateway user-facing HTTP endpoint; no privileged role or node/peer trust is required, and no `HandleJSONRPCUserMessage`/`HandleLegacyUserMessage` error needs anything beyond a normal failure condition to trigger the leak path at line 278.

### Recommendation
Apply the same redaction pattern already used elsewhere in the codebase (`confidentialrelay/handler.go`, `vault/handler.go`): for `api.HandlerError` (and any other internal-classified error code) in `gateway.go`'s `ProcessRequest`, substitute a generic message (e.g., `"internal error"`) for the wire response while still logging the full `err.Error()` server-side for diagnostics.

### Proof of Concept
1. Send a JSON-RPC request to the gateway's public HTTP endpoint whose `ServiceName()`/DON routing resolves to a handler, but where the underlying `HandleJSONRPCUserMessage`/`HandleLegacyUserMessage` call returns an error containing internal detail (e.g., a downstream config/lookup failure).
2. Observe the HTTP response body: the JSON-RPC `error.message` field contains the raw internal error string via `newError(jsonRequest.ID, api.HandlerError, err.Error())` at `core/services/gateway/gateway.go:278`, exposing internal error context to the unauthenticated caller.

### Citations

**File:** core/services/gateway/gateway.go (L270-279)
```go
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
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

**File:** core/services/gateway/network/httpserver.go (L195-245)
```go
func (s *httpServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if s.config.CORSEnabled {
		origin := r.Header.Get("Origin")
		if s.isAllowedOrigin(origin) {
			w.Header().Set("Access-Control-Allow-Origin", origin)
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		}

		// handle preflight requests
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
	}

	maxRequestBytes, err := s.config.MaxRequestBytesLimiter.Limit(r.Context())
	if err != nil {
		msg := "Failed to get request size limit"
		s.lggr.Errorw(msg, "err", err)
		http.Error(w, msg, http.StatusInternalServerError)
		return
	}
	source := http.MaxBytesReader(nil, r.Body, int64(maxRequestBytes))
	rawMessage, err := io.ReadAll(source)
	if err != nil {
		s.lggr.Error("error reading request", err)
		w.WriteHeader(http.StatusBadRequest)
		return
	}

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
	s.hMetrics.RecordRequestCount(r.Context(), httpStatusCode)

	w.Header().Set("Content-Type", s.config.ContentTypeHeader)
	w.WriteHeader(httpStatusCode)
	_, err = w.Write(rawResponse) //nolint:gosec // G705: response body is written with an explicit Content-Type, not rendered as HTML
	if err != nil {
		s.lggr.Error("error when writing response", err)
	}
}
```

**File:** core/capabilities/confidentialrelay/handler.go (L1029-1038)
```go
	h.lggr.Errorw("request error", "requestID", req.ID, "method", req.Method, "errorCode", errorCode, "err", err)
	h.metrics.requestInternalError.Add(ctx, 1, metric.WithAttributes(
		attribute.String("gateway_id", gatewayID),
		attribute.Int64("error_code", errorCode),
	))

	message := err.Error()
	if errorCode == jsonrpc.ErrInternal {
		message = internalErrorMessage
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L760-766)
```go
	switch errorCode {
	case api.FatalError:
	case api.NodeReponseEncodingError:
		h.lggr.Errorw(err.Error(), "requestID", req.ID)
		// Intentionally hide the error from the user
		err = errors.New(errorCode.String())
	case api.InvalidParamsError:
```
