### Title
Unredacted internal error messages returned to unprivileged clients via the Vault gateway handler - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
Chainlink's confidential-relay gateway handler explicitly redacts internal error messages before returning them on the wire to unprivileged callers, but the Vault capability's gateway-facing handler (`GatewayHandler`) does not apply the same redaction and instead always returns `err.Error()` verbatim in the JSON-RPC error response.

### Finding Description
`core/capabilities/confidentialrelay/handler.go`'s `errorResponse` establishes the intended defensive pattern for this codebase: internal (`jsonrpc.ErrInternal`) errors are replaced with a generic `internalErrorMessage` before being placed on the wire, so implementation details never leak to the requester: [1](#0-0) 

The Vault gateway handler's equivalent function, `GatewayHandler.errorResponse` in `core/capabilities/vault/gw_handler.go`, has no such redaction logic — it logs the error and then unconditionally puts `err.Error()` into the `jsonrpc.WireError.Message` field returned to the caller, regardless of error class: [2](#0-1) 

This function is reached from multiple call sites that wrap internal/system-level Go errors (not just user input validation errors) directly into the response:
- `handleSecretsCreate`/`handleSecretsUpdate` return `api.FatalError` (an internal-error class) wrapping whatever `secretsService.CreateSecrets`/`UpdateSecrets` returned, unredacted: [3](#0-2) 
- `handlePublicKeyGet` wraps `fmt.Errorf("failed to get public key: %w", err)` from `secretsService.GetPublicKey` under `api.HandlerError`: [4](#0-3) 
- `gatewayErrorResponse` also forwards raw pipeline/authorization errors under `api.HandlerError` for non-`InvalidVaultParamsError` cases: [5](#0-4) 

Tracing `secretsService.CreateSecrets`/`UpdateSecrets`/`GetPublicKey` to `Capability` in `core/capabilities/vault/capability.go`, the underlying error can originate from several system-level failure modes that are not intentionally sanitized at this layer:
- `handleRequest` wraps the raw error string coming back from the OCR plugin's response channel: `fmt.Errorf("error processing request %s: %w", requestID, errors.New(resp.Error))` [6](#0-5) 
- `GetPublicKey` can return low-level marshal errors: `fmt.Errorf("could not marshal public key: %w", err)` [7](#0-6) 
- `MasterPublicKeyFromSecretsService` (used by `getMasterPublicKey`, which feeds `gatewayErrorResponse`) wraps decode/unmarshal errors of internal state: [8](#0-7) 

While the OCR plugin (`core/services/ocr2/plugins/vault/plugin.go`) does apply a `userFacingError`/`vaultSecretError` sanitization step for per-secret responses that flow through `confidentialrelay`, that sanitization pattern is specific to the confidential-relay path (`vault_error.go`'s `IsUserError`/`vaulttypes.IsSecretGetSystemError`) and is not consistently reused by `GatewayHandler.errorResponse` in the vault package, which has no equivalent internal/system error classification at all before writing `err.Error()` to the wire.

This is a direct structural analog of the Microweber CVE-2022-0721 bug class (CWE-215, Insertion of Sensitive Information Into Debugging/Error Output): an unprivileged, unauthenticated-until-validated client request can trigger internal Go error strings (wrapping details about OCR/consensus failures, key marshaling failures, or public key store state) to be reflected back verbatim in the HTTP/gateway response.

### Impact Explanation
An attacker submitting crafted or edge-case requests to the Vault gateway (`MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodPublicKeyGet`, or any request that fails the authorization/pipeline stage with a non-`InvalidVaultParamsError`) can receive raw internal error text in the JSON-RPC response. Depending on what underlying dependency fails, this could surface internal identifiers, request IDs, storage/consensus state, or other implementation details that aid further attacks (CWE-215-class information disclosure). It does not by itself grant authentication/role bypass or fund movement, so severity is more moderate than the CVSS:High rating in the source advisory, but it is a genuine internal-information-disclosure defect reachable by any unprivileged caller of the gateway's Vault handler.

### Likelihood Explanation
High likelihood of triggering *some* class of internal error (e.g., transient OCR/consensus failures, malformed-but-structurally-valid requests causing marshal/unmarshal errors) given the many unredacted call sites; however, the exact sensitivity of the leaked content depends on runtime conditions and cannot be fully verified from static analysis alone — some of the wrapped errors (e.g., those already passed through `userFacingError` inside the OCR plugin) may already be sanitized before they ever reach `capability.go`/`gw_handler.go`. This uncertainty should be resolved by tracing exactly which error paths in `plugin.go`'s state-transition functions are guaranteed to invoke `userFacingError` versus those that are not.

### Recommendation
Apply the same defense used in `core/capabilities/confidentialrelay/handler.go`'s `errorResponse` to `core/capabilities/vault/gw_handler.go`'s `errorResponse`/`gatewayErrorResponse`: classify errors by error code/type and replace any non-user-facing (`api.FatalError`, `api.HandlerError` wrapping system errors) message with a generic internal-error string before writing to the wire, reserving verbatim error text for explicitly classified user-input errors (e.g., `InvalidVaultParamsError`).

### Proof of Concept
Not independently reproducible from static review alone — reproducing requires triggering a system-level failure in `secretsService.CreateSecrets`/`UpdateSecrets`/`GetPublicKey` (e.g., forcing an OCR consensus/timeout error or public-key unmarshal failure) and observing that `GatewayHandler.errorResponse` places the raw `err.Error()` string into the JSON-RPC response sent to the external caller, as shown by the code paths cited above (`gw_handler.go:275-311`, `364-373`, `388-410`).

### Citations

**File:** core/capabilities/confidentialrelay/handler.go (L1034-1038)
```go

	message := err.Error()
	if errorCode == jsonrpc.ErrInternal {
		message = internalErrorMessage
	}
```

**File:** core/capabilities/vault/gw_handler.go (L263-273)
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
```

**File:** core/capabilities/vault/gw_handler.go (L275-311)
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

**File:** core/capabilities/vault/capability.go (L234-238)
```go
	pkb, err := pubKey.Marshal()
	if err != nil {
		l.Debugw("could not marshal public key", "err", err)
		return nil, fmt.Errorf("could not marshal public key: %w", err)
	}
```

**File:** core/capabilities/vault/capability.go (L298-301)
```go
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
