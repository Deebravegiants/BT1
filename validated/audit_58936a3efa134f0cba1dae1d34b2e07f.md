I have enough evidence to answer now.

### Title
Vault gateway handler leaks raw internal error details to unprivileged clients via unredacted `errorResponse` - (File: core/capabilities/vault/gw_handler.go)

### Summary
The `Vault` capability's gateway-facing handler (`core/capabilities/vault/gw_handler.go`) forwards unredacted internal error strings from backend calls (`CreateSecrets`, `UpdateSecrets`, `DeleteSecrets`, `ListSecretIdentifiers`) directly to the unprivileged HTTP client that submitted the request, mirroring the free5GC UDM bug class of returning raw internal error text to remote callers.

### Finding Description
`GatewayHandler.errorResponse` in `core/capabilities/vault/gw_handler.go` unconditionally sets the JSON-RPC error `Message` field to `err.Error()` for every error code, with no classification or redaction logic: [1](#0-0) 

This is called from every request-handling path with wrapped internal errors, e.g. `handleSecretsCreate`/`handleSecretsUpdate` pass through `api.FatalError` with the raw backend error, and `handleSecretsDelete`/`handleSecretsList` wrap backend errors with `fmt.Errorf("failed to delete secrets: %w", err)` / `fmt.Errorf("failed to list secret identifiers: %w", err)` before forwarding: [2](#0-1) [3](#0-2) 

By contrast, the sibling handler for confidential-relay capability requests in the same codebase (`core/capabilities/confidentialrelay/handler.go`) explicitly redacts internal errors, replacing the message with a generic `internalErrorMessage` when `errorCode == jsonrpc.ErrInternal`: [4](#0-3) 

The vault gateway handler has no equivalent redaction step for any of its error codes (`api.FatalError`, `api.HandlerError`, `api.NodeReponseEncodingError`), so any error surfaced by `SecretsService` implementations (key-value store failures such as `"failed to read secret from key-value store: %w"`, `"failed to write secret to key value store: %w"`, limit-check failures, etc., seen in the underlying capability/OCR plugin code) is capable of leaking to the caller if it is not first converted into a `vaulttypes.NewUserError` by the plugin layer: [5](#0-4) 

### Impact Explanation
An unprivileged, unauthenticated-beyond-normal-allowlist workflow client submitting a `Nudm`-style gateway request (vault secrets create/update/delete/list) can trigger internal backend failures (e.g., key-value store errors, encoding failures) and receive the raw Go error text back in the JSON-RPC response. This is an information-disclosure / fingerprinting vector: it can reveal internal storage backend behavior, error phrasing, and implementation details of the vault plugin and KV store, aiding further attacks or service fingerprinting, analogous to the CVE-2025-69250 pattern of leaking `strconv.ParseInt`-style internal errors. It does not by itself grant secret disclosure, auth bypass, or fund movement, but it is a genuine "unprivileged actor observes internal error detail" issue reachable from the internet-facing gateway.

### Likelihood Explanation
Likelihood is high for triggering *some* error responses (since malformed/edge-case client input, storage contention, or resource-limit conditions are routine), but the classification of most user-facing errors is intended to go through `vaulttypes.NewUserError`/`vaultSecretError` in the plugin layer first, which somewhat limits how often true internal errors reach `errorResponse` unwrapped. The gap is real but conditional on backend failures not being pre-classified as user errors before reaching the gateway handler’s top-level `err` returned by `secretsService.CreateSecrets/UpdateSecrets/DeleteSecrets/ListSecretIdentifiers`.

### Recommendation
Apply the same redaction pattern used in `confidentialrelay/handler.go`'s `errorResponse` to `vault/gw_handler.go`'s `errorResponse`: classify errors (e.g., via `IsUserError`/`vaultSecretError`, or by introducing an explicit system/user error distinction for the top-level `CreateSecrets`/`UpdateSecrets`/`DeleteSecrets`/`ListSecretIdentifiers` return errors) and replace non-user-facing error messages with a generic constant before sending to the gateway, while still logging the full error server-side via `h.requestLogger(...).Errorw(...)`.

### Proof of Concept
1. As an authorized-but-unprivileged workflow owner, submit a `vault_secretsList` (or `secretsDelete`) gateway request that causes the underlying `SecretsService` call to fail with a genuine backend error (e.g., simulate a KV store read/write failure).
2. Observe that `handleSecretsList`/`handleSecretsDelete` wraps the error with `fmt.Errorf("failed to list secret identifiers: %w", err)` and passes it to `errorResponse`, which places `err.Error()` verbatim into the JSON-RPC `error.message` field returned over the gateway HTTP response, exposing internal error text to the client. [6](#0-5) [7](#0-6)

### Citations

**File:** core/capabilities/vault/gw_handler.go (L275-323)
```go
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
```

**File:** core/capabilities/vault/gw_handler.go (L338-349)
```go
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

**File:** core/capabilities/confidentialrelay/handler.go (L1022-1039)
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

**File:** core/services/ocr2/plugins/vault/plugin.go (L2043-2071)
```go
	secret, err := store.GetSecret(ctx, req.Id)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret from key-value store: %w", err)
	}

	if secret != nil {
		return nil, vaulttypes.NewUserError("could not write to key value store: key already exists")
	}

	count, err := store.GetSecretIdentifiersCountForOwner(ctx, req.Id.Owner)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret identifiers count for owner: %w", err)
	}

	// TODO orgID https://smartcontract-it.atlassian.net/browse/CRE-1707
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: req.Id.Owner})
	if ierr := r.cfg.MaxSecretsPerOwner.Check(ctx, count+1); ierr != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](ierr); ok {
			return nil, vaulttypes.NewUserError(fmt.Sprintf("could not write to key value store: owner %s has reached maximum number of secrets (limit=%d)", req.Id.Owner, errBoundLimited.Limit))
		}
		return nil, fmt.Errorf("failed to check max secrets per owner limit: %w", ierr)
	}

	err = store.WriteSecret(ctx, req.Id, &vaultcommon.StoredSecret{
		EncryptedSecret: encryptedSecret,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to write secret to key value store: %w", err)
	}
```
