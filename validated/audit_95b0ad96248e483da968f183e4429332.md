### Title
Internal error messages (`err.Error()`) from the Vault secrets-service are relayed verbatim to unauthenticated gateway clients - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.errorResponse` in `core/capabilities/vault/gw_handler.go` unconditionally embeds the raw Go `error.Error()` string of any internal failure into the `jsonrpc.WireError.Message` field of the response that is sent back to the gateway and ultimately to the external, unauthenticated HTTP client. This mirrors the cpp-httplib default-exception-handler flaw described in the report: whenever a handler path fails (encryption/master-key errors, key-value-store errors, JSON marshalling errors, etc.), the library's/handler's default behavior is to place the internal exception text directly on the wire with no sanitization or opt-in redaction step.

### Finding Description
`errorResponse` builds the outgoing JSON-RPC error directly from whatever `error` object was produced upstream: [1](#0-0) 

This helper is invoked from every request path in the handler with the *raw* internal error, not a sanitized user-facing message:
- `getMasterPublicKey` / `MasterPublicKeyFromSecretsService` failures: [2](#0-1) 
- `handleSecretsCreate` / `handleSecretsUpdate`, which forward `secretsService.CreateSecrets`/`UpdateSecrets` errors unchanged: [3](#0-2) 
- `handleSecretsDelete` / `handleSecretsList`, which wrap the underlying store/service error with `fmt.Errorf(..., err)` but still expose the original error text: [4](#0-3) 
- `gatewayErrorResponse`, used for auth/validation pipeline errors, also just forwards `err.Error()`: [5](#0-4) 

The response then travels back through the connector to the Gateway, and from the Gateway HTTP server directly to the requesting client as the HTTP response body, with no additional filtering: [6](#0-5)  and the top-level `gateway.ProcessRequest`/`newError` path, which similarly writes `err.Error()` straight into the wire response for parse/handler errors: [7](#0-6) 

Unlike the OCR2 plugin's consensus-facing code path, which explicitly calls a `userFacingError()` sanitizer before exposing per-secret errors (`core/services/ocr2/plugins/vault/plugin.go:1055-1062`), the node-side `GatewayHandler` in `core/capabilities/vault/gw_handler.go` has no equivalent redaction step — this is exactly the "no custom exception/error handler registered" scenario from the CVE: the default path leaks whatever error string the underlying service happened to produce.

### Impact Explanation
An unauthenticated/unprivileged external caller who reaches the Vault gateway endpoint (or the generic gateway endpoint) can trigger internal error conditions (malformed but processable requests, storage/backend failures, key-derivation failures, limiter errors, etc.) and receive the verbatim internal error string in the JSON-RPC response. Depending on what the underlying `SecretsService`/key-value store implementation returns, this can disclose internal implementation details (storage backend error text, internal identifiers, limiter internals) that were never intended to be user-facing, aiding further attacks or violating the "secret redaction" expectation for a Vault-handling component. This is a confidentiality/information-disclosure issue (matches the CVSS profile of the analog: C:L, no I/A impact).

### Likelihood Explanation
High reachability: any client that can reach the Gateway's public HTTP endpoint and route a request to the Vault handler (`vaulttypes.MethodSecretsCreate/Update/Delete/List/PublicKeyGet`) can trigger this by supplying inputs that cause the downstream service call to fail (e.g., store errors, limit-check errors, encryption errors) — no special privilege beyond passing the existing request-validation/auth pipeline is required for many of these paths (and some paths, like `getMasterPublicKey` failures and `gatewayErrorResponse` pipeline errors, occur *before* authorization succeeds).

### Recommendation
Introduce an explicit error-sanitization layer in `GatewayHandler.errorResponse` / `gatewayErrorResponse` (and the analogous `gateway.newError` path) that maps internal errors to a fixed set of safe, generic user-facing messages (similar to the `userFacingError()` helper already used in the OCR2 vault plugin), logging the raw error server-side only. Avoid passing raw `err.Error()` output into any `jsonrpc.WireError.Message` field that is transmitted to external clients.

### Proof of Concept
1. Send a `vaulttypes.MethodSecretsCreate` (or Update/Delete/List) JSON-RPC request to the Gateway's public HTTP endpoint with a payload that is valid enough to pass unmarshalling/authorization but causes the backing `SecretsService` (e.g., its key-value store) to fail (for example, exceeding `MaxSecretsPerOwner`, or triggering a storage backend error).
2. Observe the HTTP response body: the JSON-RPC `error.message` field contains the raw internal error text produced by `core/capabilities/vault/gw_handler.go`'s `errorResponse`/`gatewayErrorResponse`, e.g. `"failed to delete secrets: <internal store error>"`, rather than a generic, sanitized message.
3. Compare with the OCR2 plugin path (`core/services/ocr2/plugins/vault/plugin.go`), which sanitizes equivalent per-secret errors via `userFacingError()` before exposing them, confirming the gateway/node-side handler is missing the same redaction.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L188-198)
```go
	case vaulttypes.MethodSecretsCreate, vaulttypes.MethodSecretsUpdate:
		publicKey, pkErr := h.getMasterPublicKey(ctx)
		if pkErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pkErr)
			break
		}
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, publicKey)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
```

**File:** core/capabilities/vault/gw_handler.go (L263-272)
```go
func (h *GatewayHandler) gatewayErrorResponse(
	ctx context.Context,
	gatewayID string,
	req *jsonrpc.Request[json.RawMessage],
	err error,
) *jsonrpc.Response[json.RawMessage] {
	if IsInvalidVaultParamsError(err) {
		return h.errorResponse(ctx, gatewayID, req, api.InvalidParamsError, errors.New("invalid params error: "+err.Error()))
	}
	return h.errorResponse(ctx, gatewayID, req, api.HandlerError, err)
```

**File:** core/capabilities/vault/gw_handler.go (L280-310)
```go

	h.lggr.Debugw("Processing authorized create secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.CreateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
}

func (h *GatewayHandler) handleSecretsUpdate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.UpdateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized update secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.UpdateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
	}

	jsonResponse, err := toJSONResponse(vaultCapResponse, req.Method)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}
	return jsonResponse
```

**File:** core/capabilities/vault/gw_handler.go (L320-349)
```go
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
	}

	resultBytes, err := resp.ToJSONRPCResult()
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Result:  (*json.RawMessage)(&resultBytes),
	}
}

func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	r.Owner = authResult.AuthorizedOwner()

	h.lggr.Debugw("Processing authorized list secrets request", "request", r.String())
	resp, err := h.secretsService.ListSecretIdentifiers(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to list secret identifiers: %w", err))
	}
```

**File:** core/capabilities/vault/gw_handler.go (L388-410)
```go
func (h *GatewayHandler) errorResponse(
	ctx context.Context,
	gatewayID string,
	req *jsonrpc.Request[json.RawMessage],
	errorCode api.ErrorCode,
	err error,
) *jsonrpc.Response[json.RawMessage] {
	h.requestLogger(req, gatewayID).Errorw("gateway handler error response", "errorCode", errorCode, "error", err)
	h.metrics.requestInternalError.Add(ctx, 1, metric.WithAttributes(
		attribute.String("gateway_id", gatewayID),
		attribute.String("error", errorCode.String()),
	))

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Error: &jsonrpc.WireError{
			Code:    api.ToJSONRPCErrorCode(errorCode),
			Message: err.Error(),
		},
	}
}
```

**File:** core/services/gateway/network/httpserver.go (L233-244)
```go
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
```

**File:** core/services/gateway/gateway.go (L221-295)
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
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
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

	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
	g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.ErrorCode.String(), duration)
	g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.ErrorCode.String())

	g.lggr.Debugw("received response from handler", "handler", handlerKey, "response", response, "requestID", jsonRequest.ID)
	promRequest.WithLabelValues(response.ErrorCode.String()).Inc()
	return response.RawResponse, api.ToHTTPErrorCode(response.ErrorCode)
}
```
