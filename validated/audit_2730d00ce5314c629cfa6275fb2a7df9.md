## Finding [1](#0-0) 

### Title
Vault gateway handler leaks raw internal error strings to unprivileged callers - (File: core/capabilities/vault/gw_handler.go)

### Summary
`GatewayHandler.errorResponse` in the vault gateway handler always places the raw `err.Error()` string into the JSON-RPC `WireError.Message` field sent back to the caller through the gateway, with no distinction between user-facing and internal/system errors. This is the same bug class as CVE-2022-1120 (GitLab): an internal failure (e.g. a CI include failure / here, a KV-store or DON aggregation failure) is echoed verbatim to an untrusted client instead of being replaced with a generic message.

### Finding Description
`h.errorResponse` unconditionally does:
```go
Error: &jsonrpc.WireError{
    Code:    api.ToJSONRPCErrorCode(errorCode),
    Message: err.Error(),
},
``` [2](#0-1) 

This is called from `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`, and `handlePublicKeyGet` whenever the underlying `secretsService` call fails, wrapping errors with `api.FatalError` or `api.HandlerError`: [3](#0-2) [4](#0-3) [5](#0-4) 

The `secretsService` (backed by the OCR vault plugin) can return errors originating from the key-value store layer, e.g. `"failed to read secret from key-value store: %w"`, `"failed to write secret to key value store: %w"`, or `"failed to check request batch size limit: %w"` from validation: [6](#0-5) [7](#0-6) 

These wrapped errors are only intentionally scrubbed at the OCR-plugin observation layer for the *per-secret* response items via `userFacingError`, which substitutes a generic fallback for non-user errors: [8](#0-7) 

But the top-level error returned by `secretsService.CreateSecrets/UpdateSecrets/DeleteSecrets/ListSecretIdentifiers/GetPublicKey` (e.g. request-processing/validation/limiter errors, or any DON-level plumbing error not going through `userFacingError`) is *not* scrubbed before reaching `gw_handler.go`'s `errorResponse`, so `err.Error()` — including any `%w`-wrapped internal detail — is sent straight to the gateway response for the calling client.

This contrasts directly with the sibling handler `core/capabilities/confidentialrelay/handler.go`, which explicitly guards against this: it replaces the message with a generic `internalErrorMessage` constant whenever the JSON-RPC code is `ErrInternal`: [9](#0-8) 

The vault gateway handler has no equivalent internal/system-error redaction path — every error code (`api.FatalError`, `api.HandlerError`, `api.NodeReponseEncodingError`, etc.) surfaces the raw message.

### Impact Explanation
An unprivileged client sending vault requests through the gateway (`MethodSecretsCreate/Update/Delete/List/PublicKeyGet`) can trigger internal failure paths (e.g. limiter internal errors, KV-store errors, encoding errors) and receive the raw Go error text in the JSON-RPC response. Depending on what the underlying store/limiter/service wraps into these errors, this can leak internal implementation details (store backend errors, config/limits internals, or other diagnostic strings) to the requesting client — an information-disclosure class matching CVE-2022-1120's "missing filtering in an error message ... exposed sensitive information."

### Likelihood Explanation
Likelihood is moderate: many of today's wrapped errors are relatively benign strings (e.g. "failed to read secret from key-value store: ..."), but the pattern is systemic — any new error introduced anywhere in the `SecretsService` call chain (KV store driver, DON aggregation, limits subsystem) is passed through unfiltered to the wire unless the specific string happens not to contain sensitive detail. There's no structural safeguard, unlike the confidentialrelay handler which enforces generic messaging for internal codes.

### Recommendation
In `core/capabilities/vault/gw_handler.go`'s `errorResponse` (and/or `gatewayErrorResponse`), mirror the confidentialrelay handler's pattern: for internal/system error codes (`api.FatalError`, `api.HandlerError`, `api.NodeReponseEncodingError`), replace the wire message with a generic constant (e.g. `"internal error"`) and keep full detail only in the server-side log line (`h.requestLogger(...).Errorw(...)`, which already exists). Reserve verbatim error text for explicitly classified user errors (e.g. `IsInvalidVaultParamsError`, or vault per-secret `userFacingError`-classified user errors).

### Proof of Concept
1. Send a `secrets/create` (or update/delete/list) JSON-RPC request through the gateway as any allowlisted/authenticated-but-unprivileged workflow owner.
2. Cause the underlying `secretsService.CreateSecrets` (or list/delete) call to fail with an internal error (e.g. trigger a KV-store read/write failure, or a limiter internal error such as `"failed to check request batch size limit: %w"` from `validateWriteRequest`).
3. Observe the JSON-RPC response returned via `SendToGateway`: `resp.Error.Message` contains the raw `err.Error()` string (as asserted by the existing test at `core/capabilities/vault/gw_handler_test.go:224-233`, which checks only the error *code*, not that the message is scrubbed) rather than a generic message — demonstrating the internal detail reaches the client unfiltered.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L282-284)
```go
	vaultCapResponse, err := h.secretsService.CreateSecrets(ctx, &vaultCapRequest)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.FatalError, err)
```

**File:** core/capabilities/vault/gw_handler.go (L320-322)
```go
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to delete secrets: %w", err))
```

**File:** core/capabilities/vault/gw_handler.go (L346-348)
```go
	resp, err := h.secretsService.ListSecretIdentifiers(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to list secret identifiers: %w", err))
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

**File:** core/services/ocr2/plugins/vault/plugin.go (L1247-1253)
```go
func userFacingError(err error, fallback string) string {
	if vaulttypes.IsUserError(err) {
		return err.Error()
	}

	return fallback
}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L2043-2046)
```go
	secret, err := store.GetSecret(ctx, req.Id)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret from key-value store: %w", err)
	}
```

**File:** core/capabilities/vault/validator.go (L55-60)
```go
	if err := r.MaxRequestBatchSizeLimiter.Check(ctx, len(encryptedSecrets)); err != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](err); ok {
			return fmt.Errorf("request batch size exceeds maximum of %d: %w", errBoundLimited.Limit, err)
		}
		return fmt.Errorf("failed to check request batch size limit: %w", err)
	}
```

**File:** core/capabilities/confidentialrelay/handler.go (L1035-1038)
```go
	message := err.Error()
	if errorCode == jsonrpc.ErrInternal {
		message = internalErrorMessage
	}
```
