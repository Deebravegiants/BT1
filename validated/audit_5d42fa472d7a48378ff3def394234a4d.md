### Title
Raw Internal Error Disclosure in Vault Capability Gateway Handler - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault capability's `GatewayHandler.errorResponse` sends the full, unredacted `err.Error()` string back to the external caller through the Gateway for every `api.ErrorCode`, including internal (`api.HandlerError`) failures. Other JSON-RPC handlers in the same codebase (e.g. the confidential relay handler) explicitly sanitize internal error codes before returning them to callers; the vault gateway handler does not, so internal implementation details of the vault OCR pipeline and underlying key/value store can leak to unprivileged, internet-facing callers, analogous to the reported MongoDB error disclosure.

### Finding Description
`GatewayHandler.errorResponse` in [1](#0-0)  always sets `Message: err.Error()` regardless of the `errorCode`, with no redaction for internal-only error classes (`api.HandlerError`, `api.NodeReponseEncodingError`, etc.).

Callers into this function include `handleSecretsDelete` and `handleSecretsList`, which wrap whatever error the underlying `secretsService` (the OCR-backed `vault.Capability`) returns: [2](#0-1) 

That underlying error can originate deep in the vault OCR plugin's key/value-store access layer, e.g. `processListSecretIdentifiersRequest` wraps raw KV-store errors verbatim: `fmt.Errorf("failed to get metadata for owner: %w", err)` at [3](#0-2) , and `Capability.handleRequest` further wraps the OCR round error message: `fmt.Errorf("error processing request %s: %w", requestID, errors.New(resp.Error))` at [4](#0-3) .

This is unlike the sibling confidential-relay handler, which explicitly redacts internal errors: `if errorCode == jsonrpc.ErrInternal { message = internalErrorMessage }` at [5](#0-4) , and the gateway-side vault handler's own `constructErrorResponse`, which normalizes several codes but still passes through internal handler errors unsanitized at [6](#0-5) . The `GatewayHandler` in `core/capabilities/vault` has no equivalent redaction path at all.

The resulting `jsonrpc.Response` is sent unmodified to the Gateway (`h.gatewayConnector.SendToGateway`) and from there relayed toward the originating external/unprivileged caller, since the Gateway is the internet-facing entry point for Vault secret operations.

### Impact Explanation
Malformed or edge-case Vault requests (e.g. requests for owners/keys that trigger KV-store lookup failures, OCR aggregation errors, or timeout conditions) can cause internal implementation details — underlying storage error text, internal request IDs, and OCR pipeline error strings — to be returned verbatim to an external caller via the Gateway. This mirrors the reported bug class (verbose backend error disclosure to unauthenticated/unprivileged callers), aiding reconnaissance of the Vault DON's internal architecture (storage backend behavior, OCR consensus error paths) and expanding the attack surface for further targeted attacks against the Vault capability.

### Likelihood Explanation
Likelihood is moderate: triggering it requires only sending a syntactically valid but semantically edge-case `SecretsDelete`/`SecretsList` (or `PublicKeyGet`) JSON-RPC request through the Gateway that causes `secretsService` to return a non-nil error (e.g. an owner with corrupted/missing metadata, or transient OCR/store errors), which does not require bypassing authentication — the authorization layer only checks whether the request is well-formed and allow-listed, not what error the downstream store may raise.

### Recommendation
Apply the same redaction pattern used in `confidentialrelay/handler.go` to `GatewayHandler.errorResponse` in `core/capabilities/vault/gw_handler.go`: for internal error codes (e.g. `api.HandlerError`, `api.NodeReponseEncodingError`), replace `err.Error()` with a generic, non-identifying message while still logging the full error server-side with a correlation/request ID for debugging.

### Proof of Concept
1. Send a `secretsList` or `secretsDelete` JSON-RPC request through the Gateway for an owner/key combination that causes the underlying vault KV store to return an error (e.g. corrupted metadata entry, simulated store failure).
2. Observe the response returned by the Gateway to the (external, allow-listed but otherwise unprivileged) caller: the `error.message` field contains the raw wrapped error text produced deep in `core/services/ocr2/plugins/vault/plugin.go`'s `processListSecretIdentifiersRequest`/`stateTransitionDeleteSecretsRequest`, rather than a generic message, because `GatewayHandler.errorResponse` (`core/capabilities/vault/gw_handler.go:388-410`) never redacts it for `api.HandlerError` codes as `constructErrorResponse`/`errorResponse` do in the confidential relay handlers.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L313-349)
```go
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

**File:** core/services/ocr2/plugins/vault/plugin.go (L1148-1156)
```go
func (r *ReportingPlugin) processListSecretIdentifiersRequest(ctx context.Context, seqNr uint64, requestID string, reader ReadKVStore, req *vaultcommon.ListSecretIdentifiersRequest) (*vaultcommon.ListSecretIdentifiersResponse, error) {
	if err := r.validateListSecretIdentifiersOwnerNonempty(req); err != nil {
		return nil, err
	}

	md, err := reader.GetMetadata(ctx, req.Owner)
	if err != nil {
		return nil, fmt.Errorf("failed to get metadata for owner: %w", err)
	}
```

**File:** core/capabilities/vault/capability.go (L279-306)
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
}
```

**File:** core/capabilities/confidentialrelay/handler.go (L1022-1038)
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
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L776-797)
```go
func (h *handler) constructErrorResponse(req jsonrpc.Request[json.RawMessage], errorCode api.ErrorCode, err error) gwhandlers.UserCallbackPayload {
	//nolint:exhaustive // do not modify other error codes
	switch errorCode {
	case api.NodeReponseEncodingError:
		err = errors.New(errorCode.String())
	case api.InvalidParamsError:
		err = fmt.Errorf("invalid params error: %w", err)
	case api.UnsupportedMethodError:
		err = fmt.Errorf("unsupported method(%s): %w", req.Method, err)
	case api.UserMessageParseError:
		err = fmt.Errorf("user message parse error: %w", err)
	}
	return gwhandlers.UserCallbackPayload{
		RawResponse: h.codec.EncodeNewErrorResponse(
			req.ID,
			api.ToJSONRPCErrorCode(errorCode),
			err.Error(),
			nil,
		),
		ErrorCode: errorCode,
	}
}
```
