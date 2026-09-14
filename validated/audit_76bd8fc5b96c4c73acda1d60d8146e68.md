## Title
Vault gateway handler leaks raw internal error messages to unprivileged callers via unredacted JSON-RPC error responses - (File: `core/capabilities/vault/gw_handler.go`)

## Summary
The Flight advisory describes a default error handler that serializes the raw exception message, code, and full stack trace into the HTTP response with no debug gating, leaking internal paths/secrets to any unprivileged caller. The Chainlink Vault `GatewayHandler` has an analogous unrestricted error-propagation path: `errorResponse()` always places the *raw* `err.Error()` string into the JSON-RPC response sent back over the gateway to the (unprivileged) requester, with no redaction, unlike the sibling `confidentialrelay` handler which explicitly redacts internal errors.

## Finding Description
`GatewayHandler.errorResponse` in `core/capabilities/vault/gw_handler.go` builds the wire error unconditionally from the underlying Go error: [1](#0-0) 

Every caller of `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`, and `handlePublicKeyGet` funnels arbitrary internal failures — including errors from `secretsService.CreateSecrets/UpdateSecrets/DeleteSecrets/ListSecretIdentifiers/GetPublicKey` — straight into this function, e.g.: [2](#0-1) 

Those underlying errors originate from the OCR request/response pipeline in `Capability.handleRequest`, which wraps whatever error string the DON reports back (`resp.Error`) verbatim: [3](#0-2) 

This is reachable by any client that can reach the gateway's Vault methods (`vaulttypes.MethodSecretsCreate/Update/Delete/List`) — i.e. an unprivileged, internet-facing request path through `GatewayHandler.HandleGatewayMessage`: [4](#0-3) 

By contrast, the sibling `confidentialrelay` handler on the same gateway/DON boundary explicitly redacts internal errors before returning them to the caller: [5](#0-4) 

`gw_handler.go`'s `errorResponse`/`gatewayErrorResponse` have no equivalent redaction for `api.HandlerError`/`api.FatalError` classes, and there is no debug/production gating comparable to Flight's `flight.debug` fix — every internal error message (which can include backend storage details, internal identifiers, or other implementation detail interpolated by lower layers) is returned as-is.

## Impact Explanation
Any error surfaced from the secrets-storage backend, OCR handler, or validation layers is echoed verbatim to the requesting client in the JSON-RPC `error.message` field. This can disclose internal implementation details (error strings from storage/backends, internal request IDs, validation internals) to an unprivileged caller, matching the CWE-209 information-exposure class of the advisory, though severity here depends on what detail the underlying `secretsService`/OCR errors actually carry.

## Likelihood Explanation
Any client capable of sending a Vault-related gateway request (create/update/delete/list secrets, get public key) that triggers a backend or handler-level failure will receive the unredacted error text by design of the current code path — no special conditions or privileges are required beyond making a request that errors out.

## Recommendation
Mirror the pattern already used in `core/capabilities/confidentialrelay/handler.go`: classify errors and return only a generic/internal message for internal error classes (`api.HandlerError`, `api.FatalError`, `api.NodeReponseEncodingError`), reserving detailed messages for classes that are genuinely user-input-driven (e.g. `api.InvalidParamsError` / `api.UserMessageParseError`). Log the full error server-side via `h.requestLogger(...).Errorw(...)` (already done) but do not place raw `err.Error()` into the wire response for internal-error classes in `GatewayHandler.errorResponse`.

## Proof of Concept
1. Send a `vault_secretsCreate`/`vault_secretsUpdate`/`vault_secretsDelete`/`vault_secretsList` JSON-RPC request through the gateway that passes authorization/validation but fails at the `secretsService`/OCR layer (e.g. induce a backend/storage error).
2. Observe the JSON-RPC response returned to the gateway/client: `error.message` contains the raw underlying error string built in `core/capabilities/vault/gw_handler.go` `errorResponse()`, potentially including internal backend detail, rather than a generic message.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-236)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

	switch req.Method {
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
		authResult = authorized.AuthResult
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}

	if response == nil {
		switch req.Method {
		case vaulttypes.MethodSecretsCreate:
			response = h.handleSecretsCreate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsUpdate:
			response = h.handleSecretsUpdate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsDelete:
			response = h.handleSecretsDelete(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsList:
			response = h.handleSecretsList(ctx, gatewayID, req, authResult)
		}
	}

	if err = h.gatewayConnector.SendToGateway(ctx, gatewayID, response); err != nil {
		reqLggr.Errorw("Failed to send message to gateway", "error", err)
		return err
	}

	reqLggr.Infow("Sent message to gateway", "resp", response)
	h.metrics.requestSuccess.Add(ctx, 1, metric.WithAttributes(
		attribute.String("gateway_id", gatewayID),
	))
	return nil
}
```

**File:** core/capabilities/vault/gw_handler.go (L313-323)
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

**File:** core/capabilities/vault/capability.go (L295-304)
```go
	case resp := <-respCh:
		s.lggr.Debugw("received response for request", "requestID", requestID, "error", resp.Error)
		respAt := s.clock.Now()
		if resp.Error != "" {
			s.lifecycle.FinalizeResponseError(ctx, requestID, respAt, resp.Error)
			return nil, fmt.Errorf("error processing request %s: %w", requestID, errors.New(resp.Error))
		}

		s.lifecycle.FinalizeSuccess(ctx, requestID, respAt)
		return resp, nil
```

**File:** core/capabilities/confidentialrelay/handler.go (L1022-1048)
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
```
