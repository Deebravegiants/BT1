Audit Report

## Title
Unredacted internal error messages returned to unprivileged clients via the Vault gateway handler - (File: `core/capabilities/vault/gw_handler.go`)

## Summary
`core/capabilities/vault/gw_handler.go`'s `GatewayHandler.errorResponse` unconditionally places `err.Error()` into the `jsonrpc.WireError.Message` field, unlike the analogous `Handler.errorResponse` in `core/capabilities/confidentialrelay/handler.go`, which redacts internal-class errors (`jsonrpc.ErrInternal`) to a generic message before writing to the wire. Multiple call sites (`handleSecretsCreate`, `handleSecretsUpdate`, `handlePublicKeyGet`, `gatewayErrorResponse`) forward raw Go error strings originating from internal failure modes (OCR/consensus errors, key marshal/unmarshal failures, state decode errors) verbatim through this path.

## Finding Description
`GatewayHandler.errorResponse` (`core/capabilities/vault/gw_handler.go:388-410`) logs the error and writes `err.Error()` directly into `jsonrpc.WireError.Message` regardless of error classification, whereas `confidentialrelay/handler.go`'s `errorResponse` (`core/capabilities/confidentialrelay/handler.go:1022-1049`) substitutes a generic `internalErrorMessage` when `errorCode == jsonrpc.ErrInternal`. The vault gateway handler has no equivalent classification step.

Confirmed call sites that pass unredacted internal errors:
- `handleSecretsCreate`/`handleSecretsUpdate` wrap `secretsService.CreateSecrets`/`UpdateSecrets` errors under `api.FatalError` (`gw_handler.go:283-284`, `302-303`), which can originate from `capability.go`'s `handleRequest`, wrapping the raw OCR plugin response error string (`core/capabilities/vault/capability.go:298-301`).
- `handlePublicKeyGet` wraps `GetPublicKey` errors, including marshal failures (`capability.go:234-238`), under `api.HandlerError` (`gw_handler.go:370-373`).
- `gatewayErrorResponse` forwards `getMasterPublicKey`/`MasterPublicKeyFromSecretsService` decode/unmarshal errors (`gateway_vault_request_processor.go:330-349`) under `api.HandlerError` unless classified as `InvalidVaultParamsError` (`gw_handler.go:263-273`).

However, this node-side `GatewayHandler` response is **not sent directly to the external client**. It is sent to the gateway node via `SendToGateway`, and the gateway-side handler (`core/services/gateway/handlers/vault/handler.go`) requires a Byzantine-fault-tolerant quorum (`h.aggregator.Aggregate`, `HandleNodeMessage`, lines 480-534) of matching signed node responses before forwarding a result to the requesting user (`sendSuccessResponse`, lines 585-611). Test `TestVaultHandler_HandleNodeMessage_StillAcceptsErrorOnlyResponses` (`handler_test.go:1220-1270`) confirms that once quorum on an identical `jsonrpc.WireError.Message` string is reached across signed node responses, that raw message text is indeed forwarded unmodified to the calling client. This means the claim's exploit path is real *only when a deterministic, cross-node-consistent internal failure occurs* (e.g., a consistent marshal/unmarshal bug, or a state condition shared by enough honest nodes to reach quorum) — a transient or per-node-random internal error would not reach quorum and would instead surface as `errInsufficientResponsesForQuorum` or a gateway-generated `api.FatalError` (which does not embed the underlying per-node error text, per `handler.go:516-524`).

Existing defenses reviewed and found insufficient: the vault gateway handler applies no error-classification/redaction logic analogous to `confidentialrelay/handler.go`, and the gateway-side aggregator's quorum requirement reduces likelihood but does not eliminate the disclosure — it only requires the underlying failure to be reproducible/deterministic across a threshold of DON nodes, which is plausible for bugs like the cited marshal/unmarshal error paths.

## Impact Explanation
This is a genuine CWE-215-class internal information disclosure: an unprivileged (though request-validated) caller of the Vault gateway can, under a deterministic internal failure condition, receive raw Go error strings that may reveal internal state, request IDs, or implementation details. It does not achieve authentication bypass, key/secret exfiltration, or fund movement by itself, so it falls short of the higher-severity in-scope impact categories (auth bypass, secret exfiltration, unauthorized fund movement), but it is a legitimate defense-in-depth gap matching a known internal-error-redaction pattern already implemented elsewhere in the same codebase (`confidentialrelay/handler.go`).

## Likelihood Explanation
Moderate, not high: unlike the original claim's assumption that any single Go node error is reflected to the client, the actual code path (`core/services/gateway/handlers/vault/handler.go` aggregator/quorum logic) requires that at least a quorum (2f+1/BFT threshold) of independent DON nodes independently produce byte-identical error text before it is forwarded to the user. This significantly narrows the practically exploitable scenarios to deterministic, cross-node-shared internal failures (e.g., a shared serialization bug or a common malformed-state condition), rather than arbitrary or node-specific internal errors (e.g., timing-dependent OCR consensus failures, which would likely differ per node and fail to reach quorum).

## Recommendation
Apply the same error-classification/redaction pattern used in `core/capabilities/confidentialrelay/handler.go`'s `errorResponse` to `core/capabilities/vault/gw_handler.go`'s `errorResponse`/`gatewayErrorResponse`: classify errors by `api.ErrorCode` and replace messages for internal/system-error classes (`api.FatalError`, `api.HandlerError` wrapping non-`InvalidVaultParamsError` errors) with a generic internal-error string before writing to `jsonrpc.WireError.Message`, reserving verbatim text for explicitly classified user-input errors (`api.UserMessageParseError`, `api.InvalidParamsError`).

## Proof of Concept
1. Force a deterministic internal failure shared across a quorum of Vault DON nodes — e.g., cause `secretsService.GetPublicKey` or `MasterPublicKeyFromSecretsService` to hit the same unmarshal/decode error path on enough nodes (reproducible via corrupting the persisted public key state consistently, or via a unit test directly invoking `GatewayHandler.errorResponse`/`handlePublicKeyGet` with a mocked `secretsService` returning a wrapped internal error).
2. Observe that `GatewayHandler.errorResponse` (`gw_handler.go:388-410`) places `err.Error()` verbatim into the `jsonrpc.WireError.Message` sent via `SendToGateway`.
3. Confirm end-to-end disclosure using the existing test pattern in `core/services/gateway/handlers/vault/handler_test.go`'s `TestVaultHandler_HandleNodeMessage_StillAcceptsErrorOnlyResponses`, adapted to submit quorum-matching signed responses containing the raw internal error text, and assert that `callback.Wait` returns the unredacted message to the "client" callback. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** core/capabilities/vault/gw_handler.go (L263-311)
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
```

**File:** core/capabilities/vault/gw_handler.go (L364-373)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	resp, err := h.secretsService.GetPublicKey(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to get public key: %w", err))
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

**File:** core/capabilities/vault/capability.go (L234-238)
```go
	pkb, err := pubKey.Marshal()
	if err != nil {
		l.Debugw("could not marshal public key", "err", err)
		return nil, fmt.Errorf("could not marshal public key: %w", err)
	}
```

**File:** core/capabilities/vault/capability.go (L296-301)
```go
		s.lggr.Debugw("received response for request", "requestID", requestID, "error", resp.Error)
		respAt := s.clock.Now()
		if resp.Error != "" {
			s.lifecycle.FinalizeResponseError(ctx, requestID, respAt, resp.Error)
			return nil, fmt.Errorf("error processing request %s: %w", requestID, errors.New(resp.Error))
		}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L330-349)
```go
// MasterPublicKeyFromSecretsService loads the vault master public key from a secrets service.
func MasterPublicKeyFromSecretsService(ctx context.Context, secretsService vaulttypes.SecretsService) (*tdh2easy.PublicKey, error) {
	resp, err := secretsService.GetPublicKey(ctx, &vaultcommon.GetPublicKeyRequest{})
	if err != nil {
		return nil, fmt.Errorf("failed to get vault public key: %w", err)
	}
	if resp == nil || resp.PublicKey == "" {
		return nil, errors.New("vault public key is unavailable")
	}

	masterPublicKeyBytes, err := hex.DecodeString(resp.PublicKey)
	if err != nil {
		return nil, fmt.Errorf("failed to decode vault public key: %w", err)
	}

	masterPublicKey := &tdh2easy.PublicKey{}
	if err := masterPublicKey.Unmarshal(masterPublicKeyBytes); err != nil {
		return nil, fmt.Errorf("failed to unmarshal vault public key: %w", err)
	}
	return masterPublicKey, nil
```

**File:** core/services/gateway/handlers/vault/handler.go (L480-534)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	if !h.nodeRateLimiter.Allow(nodeAddr) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}

	ar := h.getActiveRequest(resp.ID)
	if ar == nil {
		// Request is not found, so we don't need to send a response to the user
		// This can happen if a slow node responds after the request has already been completed
		l.Debugw("no pending request found for ID")
		return nil
	}

	if resp.Result != nil && resp.Error != nil {
		l.Errorw("node response contains both a result and an error, dropping", "nodeAddr", nodeAddr)
		h.recordInvalidNodeResponseEnvelope(ctx, "node_response_result_and_error")
		return nil //nolint:nilerr // tampered envelope is intentionally dropped; handling succeeded so there is no error to report
	}

	if resp.Method != ar.req.Method {
		l.Errorw("node response method does not match request method, dropping", "nodeAddr", nodeAddr, "responseMethod", resp.Method, "requestMethod", ar.req.Method)
		h.recordInvalidNodeResponseEnvelope(ctx, "node_response_method_mismatch")
		return nil
	}

	ok := ar.addResponseForNode(nodeAddr, resp)
	if !ok {
		l.Errorw("duplicate response from node, ignoring", "nodeAddr", nodeAddr)
		return nil
	}

	copiedResponses := ar.copiedResponses()
	resp, err := h.aggregator.Aggregate(ctx, l, ar.req.ID, copiedResponses, resp)
	switch {
	case errors.Is(err, errInsufficientResponsesForQuorum):
		l.Debugw("aggregating responses, waiting for other nodes...", "error", err)
		return nil
	case err != nil:
		l.Error("quorum unobtainable, returning response to user...", "error", err, "responses", maps.Values(copiedResponses))
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, err, nil))
	}

	switch resp.Method {
	case vaulttypes.MethodPublicKeyGet:
		h.tryCachePublicKeyResponse(resp, l)
	default:
		// Do nothing for other methods
	}

	return h.sendSuccessResponse(ctx, l, ar, resp)
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L585-611)
```go
func (h *handler) sendSuccessResponse(ctx context.Context, l logger.Logger, ar *activeRequest, resp *jsonrpc.Response[json.RawMessage]) error {
	// Strip the owner prefix from the response ID before sending it back to the user
	// This ensures compliance with JSONRPC 2.0 spec, which requires response id to match request id
	index := strings.Index(resp.ID, vaulttypes.RequestIDSeparator)
	if index != -1 {
		resp.ID = resp.ID[index+2:]
	}
	rawResponse, err := jsonrpc.EncodeResponse(resp)
	if err != nil {
		l.Errorw("failed to encode response", "error", err)
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.NodeReponseEncodingError, fmt.Errorf("failed to marshal response: %w", err), nil))
	}

	var errorCode api.ErrorCode
	if resp.Error != nil {
		errorCode = api.FromJSONRPCErrorCode(resp.Error.Code)
	} else {
		errorCode = api.NoError
	}

	l.Debugw("issued user callback", "errorCode", errorCode)
	successResp := gwhandlers.UserCallbackPayload{
		RawResponse: rawResponse,
		ErrorCode:   errorCode,
	}
	return h.sendResponse(ctx, ar, successResp)
}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1220-1270)
```go
func TestVaultHandler_HandleNodeMessage_StillAcceptsErrorOnlyResponses(t *testing.T) {
	t.Parallel()
	h, callback, _, _ := setupHandler(t)

	signers := []string{
		"d6da96fe596705b32bc3a0e11cdefad77feaad79000000000000000000000000",
		"327aa349c9718cd36c877d1e90458fe1929768ad000000000000000000000000",
		"e9bf394856d73402b30e160d0e05c847796f0e29000000000000000000000000",
		"efd5bdb6c3256f04489a6ca32654d547297f48b9000000000000000000000000",
	}
	nodes := makeNodes(t, signers)
	mcr := &mockCapabilitiesRegistry{F: 1, Nodes: nodes}
	h.(*handler).aggregator = &baseAggregator{
		capabilitiesRegistry: mcr,
		metrics:              h.(*handler).metrics,
		vaultHandlerDonID:    h.(*handler).donConfig.DonID,
	}

	const requestID = "req-a2-err-only"
	req := jsonrpc.Request[json.RawMessage]{
		ID:     requestID,
		Method: vaulttypes.MethodSecretsCreate,
	}
	_, err := h.(*handler).newActiveRequest(req, callback)
	require.NoError(t, err)

	errorResp := jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      requestID,
		Method:  vaulttypes.MethodSecretsCreate,
		Error: &jsonrpc.WireError{
			Code:    api.ToJSONRPCErrorCode(api.InvalidParamsError),
			Message: "invalid params error: secret ID must not be nil",
		},
	}
	for _, nodeAddr := range []string{"0xn0", "0xn1", "0xn2"} {
		r := errorResp
		require.NoError(t, h.HandleNodeMessage(t.Context(), &r, nodeAddr))
	}

	resp, err := callback.Wait(t.Context())
	require.NoError(t, err)
	assert.Equal(t, api.InvalidParamsError, resp.ErrorCode)

	var errResponse jsonrpc.Response[json.RawMessage]
	require.NoError(t, json.Unmarshal(resp.RawResponse, &errResponse))
	assert.Nil(t, errResponse.Result)
	require.NotNil(t, errResponse.Error)
	assert.Equal(t, api.ToJSONRPCErrorCode(api.InvalidParamsError), errResponse.Error.Code)
	assert.Nil(t, h.(*handler).getActiveRequest(requestID))
}
```
