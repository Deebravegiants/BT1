### Title
Unmasked internal error messages returned to unauthenticated/unauthorized gateway callers in the Vault gateway handler - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
The vault gateway handler's `errorResponse` writes the raw Go error string (`err.Error()`) directly onto the JSON-RPC wire response for every error path, regardless of error class or origin, in contrast to the sibling `confidentialrelay` handler which explicitly redacts internal error text before it reaches the caller.

### Finding Description
`GatewayHandler.errorResponse` in `core/capabilities/vault/gw_handler.go` always sets `Message: err.Error()` on the outgoing `jsonrpc.WireError`, with no distinction between user-facing/validation errors and internal/system errors: [1](#0-0) 

This function is invoked from every handler branch — `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`, `handlePublicKeyGet`, and `gatewayErrorResponse` (used for master-public-key retrieval and request-processor/auth pipeline failures): [2](#0-1) 

Several of these wrap errors from `h.secretsService` (backed by the OCR vault plugin via `Capability.handleRequest`), which can surface internal/system failure strings from `resp.Error` (OCR consensus/report errors, transport failures, etc.) rather than sanitized user messages: [3](#0-2) 

This is a real regression relative to the pattern established elsewhere in the same codebase. `confidentialrelay/handler.go`'s `errorResponse` explicitly replaces the message with a generic `internalErrorMessage` when `errorCode == jsonrpc.ErrInternal`: [4](#0-3) 

The codebase also has a documented, deliberate secret/system-error redaction convention (`vaultSecretError`, `IsUserError`) used specifically to prevent internal vault/system failure text from leaking to callers: [5](#0-4) 

The vault `GatewayHandler.errorResponse`, however, applies none of this classification — every error, whether from JSON parsing, request-processor/authorization checks, or the underlying OCR-backed `secretsService`, is passed through verbatim.

### Impact Explanation
This maps to CWE-209 (Generation of Error Message Containing Sensitive Information), the same class as the referenced Apache Airflow advisory: callers hitting the vault gateway endpoint (`MethodSecretsCreate/Update/Delete/List/PublicKeyGet`) can receive raw internal error text in the JSON-RPC error response instead of a generic message. Depending on what `secretsService`/OCR plugin errors contain (internal state, consensus failure details, node identifiers, or other backend-specific strings), this could leak information useful to an attacker probing the node, and is inconsistent with the explicit sanitization the team applies in the parallel `confidentialrelay` path. This is an information-disclosure issue, not by itself an authentication/authorization bypass — impact is bounded to whatever detail ends up inside error strings from `secretsService`/`ProcessRequest`, which I could not fully enumerate (their exact string content for all system-failure cases sits deeper in the OCR plugin than I was able to trace in the available time).

### Likelihood Explanation
Any client able to reach the vault gateway endpoint and trigger an error path (malformed params, invalid secret ops, transient OCR/consensus failures) will receive whatever `err.Error()` produces, since there is no gating on error origin in `errorResponse`. Given this is on every failure branch of every vault RPC method, likelihood of *some* extra information reaching a caller is high; the sensitivity of what specifically leaks is uncertain without inspecting every possible error string producible by `secretsService`, `requestProcessor.ProcessRequest`, and `MasterPublicKeyFromSecretsService`.

### Recommendation
Apply the same masking convention used in `core/capabilities/confidentialrelay/handler.go`: classify errors from `secretsService`/`requestProcessor` as user vs. system (reusing or mirroring `vaultSecretError`/`IsUserError`), and only pass through the raw message when the error is a known, safe, user-facing validation/parse error (`api.UserMessageParseError`, `api.InvalidParamsError`). For all other codes (`api.HandlerError`, `api.FatalError`, `api.NodeReponseEncodingError` when wrapping unexpected internal failures), replace the message with a generic constant before writing it into the `jsonrpc.WireError`, while still logging the full error server-side as `errorResponse` already does.

### Proof of Concept
Not applicable as a runnable PoC given the sandboxed/read-only nature of this investigation; the vulnerable code path is directly demonstrable by tracing: any request to `MethodSecretsCreate`/`Update`/`Delete`/`List`/`PublicKeyGet` that causes `h.secretsService.*` or `h.requestProcessor.ProcessRequest` to return a non-nil error will have that error's `.Error()` string written verbatim into the wire response by `GatewayHandler.errorResponse` (`core/capabilities/vault/gw_handler.go:388-410`), with no redaction step, unlike the equivalent path in `core/capabilities/confidentialrelay/handler.go:1022-1049`.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L263-336)
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
}

func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

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
}

func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
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

**File:** core/capabilities/vault/capability.go (L279-305)
```go
func (s *Capability) handleRequest(ctx context.Context, requestID string, request proto.Message) (*vaulttypes.Response, error) {
	s.lifecycle.RecordReceived(ctx, requestID, s.clock.Now())
	respCh := make(chan *vaulttypes.Response, 1)
	s.handler.SendRequest(ctx, &vaulttypes.Request{
		Payload:      request,
		ResponseChan: respCh,

		ExpiryTimeVal: s.clock.Now().Add(s.expiresAfter),
		IDVal:         requestID,
	})
	s.lggr.Debugw("sent request to OCR handler", "requestID", requestID)
	select {
	case <-ctx.Done():
		s.lggr.Debugw("request timed out", "requestID", requestID, "error", ctx.Err())
		s.lifecycle.FinalizeTimeout(ctx, requestID)
		return nil, ctx.Err()
	case resp := <-respCh:
		s.lggr.Debugw("received response for request", "requestID", requestID, "error", resp.Error)
		respAt := s.clock.Now()
		if resp.Error != "" {
			s.lifecycle.FinalizeResponseError(ctx, requestID, respAt, resp.Error)
			return nil, fmt.Errorf("error processing request %s: %w", requestID, errors.New(resp.Error))
		}

		s.lifecycle.FinalizeSuccess(ctx, requestID, respAt)
		return resp, nil
	}
```

**File:** core/capabilities/confidentialrelay/handler.go (L1022-1049)
```go
func (h *Handler) errorResponse(
	ctx context.Context,
	gatewayID string,
	req *jsonrpc.Request[json.RawMessage],
	errorCode int64,
	err error,
) *jsonrpc.Response[json.RawMessage] {
	h.lggr.Errorw("request error", "requestID", req.ID, "method", req.Method, "errorCode", errorCode, "err", err)
	h.metrics.requestInternalError.Add(ctx, 1, metric.WithAttributes(
		attribute.String("gateway_id", gatewayID),
		attribute.Int64("error_code", errorCode),
	))

	message := err.Error()
	if errorCode == jsonrpc.ErrInternal {
		message = internalErrorMessage
	}

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Error: &jsonrpc.WireError{
			Code:    errorCode,
			Message: message,
		},
	}
}
```

**File:** core/capabilities/confidentialrelay/vault_error.go (L10-21)
```go
// vaultSecretError wraps a per-secret error returned by the vault DON in a
// SecretResponse.Error field. The vault OCR plugin classifies user-caused
// failures (e.g. "key does not exist") as userError and surfaces the raw
// message through userFacingError. System failures are replaced with a generic
// fallback (vaulttypes.SecretGetSystemErrorFallback) so their details do not
// leak.
//
// By the time the relay handler sees the string the Go type is gone (protobuf
// boundary), so translateVaultResponse re-wraps it here with an explicit isUser
// flag set at construction time. The handler checks the flag via IsUserError to
// map user errors to jsonrpc.ErrInvalidParams and system errors to
// jsonrpc.ErrInternal.
```
