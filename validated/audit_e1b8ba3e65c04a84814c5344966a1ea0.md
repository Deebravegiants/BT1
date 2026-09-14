## Finding

### Title
Unsanitized internal error messages leaked to unprivileged callers via Vault GatewayHandler - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
The Apache Superset advisory (CVE-2024-53948, CWE-209) concerns raw backend/database error text being surfaced verbatim to end users, exposing internal metadata. The Chainlink Vault `GatewayHandler` (used by the enclave/DON-side vault capability, distinct from the outer `core/services/gateway/handlers/vault` package) exhibits the same class of bug: it forwards the raw `.Error()` string of internal service/library failures directly onto the JSON-RPC wire response returned to the calling client, with no redaction for most error paths.

### Finding Description
`GatewayHandler.errorResponse` puts `err.Error()` directly into the `jsonrpc.WireError.Message` field with no sanitization for any error code: [1](#0-0) 

Every call site that talks to the underlying `vaulttypes.SecretsService` (`h.secretsService.CreateSecrets/UpdateSecrets/DeleteSecrets/ListSecretIdentifiers/GetPublicKey`) forwards whatever error it receives straight into `errorResponse` with `api.FatalError` or `api.HandlerError`, both of which fall through the switch untouched (unlike `api.NodeReponseEncodingError`, which is deliberately masked in the sibling package): [2](#0-1) 

Contrast this with the intentional redaction pattern used elsewhere in the codebase for the exact same class of error:
- `core/services/gateway/handlers/vault/handler.go`'s `errorResponse` explicitly comments "Intentionally hide the error from the user" for `NodeReponseEncodingError`. [3](#0-2) 
- `core/capabilities/confidentialrelay/handler.go`'s `errorResponse` substitutes a generic `internalErrorMessage` constant whenever `errorCode == jsonrpc.ErrInternal`. [4](#0-3) 

The underlying `SecretsService` (implemented by `Capability` in `core/capabilities/vault/capability.go`) can surface unredacted internal details through this path — e.g., key-value store read/write failures such as `"failed to read secret from key-value store: %w"` and `"failed to write secret to key value store: %w"` from the OCR2 vault plugin, which wrap underlying storage errors: [5](#0-4) 

Because `GatewayHandler.HandleGatewayMessage` calls `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`/`handleSecretsList` after only gateway-level authorization (JWT/allowlist check, not an "internal operator" trust boundary), any caller who can reach the gateway and pass that authorization check receives these raw internal messages on failure: [6](#0-5) 

### Impact Explanation
Verbose internal error strings (storage backend errors, internal validation states, wrapped Go error chains) are returned to external, unprivileged-but-authorized callers of the vault gateway. This can disclose internal implementation details, storage engine identifiers, or transient system state that aids further attacks or violates confidentiality guarantees the rest of the codebase clearly intends to uphold (as evidenced by the deliberate redaction done in the sibling handler and the confidential-relay handler). This matches CWE-209 (Generation of Error Message Containing Sensitive Information).

### Likelihood Explanation
Any transient backend failure (KV store errors, marshal/unmarshal failures, downstream service errors) during `CreateSecrets`, `UpdateSecrets`, `DeleteSecrets`, `ListSecretIdentifiers`, or `GetPublicKey` will trigger this path. Since these are ordinary operational failure modes (not requiring privilege escalation or a malicious peer), the likelihood of the message-leak firing is moderate-to-high whenever the backing store experiences any error, and it is entirely deterministic and remotely observable by any client with gateway authorization.

### Recommendation
Apply the same redaction pattern already used elsewhere in the codebase: in `GatewayHandler.errorResponse` (and/or at each call site in `handleSecretsCreate/Update/Delete/List/handlePublicKeyGet`), classify errors as user-facing vs. internal (mirroring the `IsUserError`/`vaultSecretError` pattern in `core/capabilities/confidentialrelay/vault_error.go`), log the full error server-side, and return only a generic fallback message (e.g., a constant like `internalErrorMessage`) to the caller for internal/system-origin errors while preserving detail only for genuine, pre-classified user validation errors.

### Proof of Concept
1. Trigger any backend failure reachable through `SecretsService` (e.g., simulate a KV-store error during `CreateSecrets`/`DeleteSecrets`, or any failure not filtered as `InvalidVaultParamsError`).
2. Send a `vault_secretsCreate` (or equivalent) JSON-RPC request through the gateway with valid authorization/allowlisting.
3. Observe the JSON-RPC error response returned via `GatewayHandler.errorResponse` — the `Message` field contains the raw wrapped error (e.g., `"failed to delete secrets: failed to read secret from key-value store: ..."`), exposing internal implementation detail rather than a generic message.

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

**File:** core/capabilities/vault/gw_handler.go (L275-336)
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

**File:** core/services/gateway/handlers/vault/handler.go (L754-775)
```go
func (h *handler) errorResponse(
	req jsonrpc.Request[json.RawMessage],
	errorCode api.ErrorCode,
	err error,
	data []byte,
) gwhandlers.UserCallbackPayload {
	switch errorCode {
	case api.FatalError:
	case api.NodeReponseEncodingError:
		h.lggr.Errorw(err.Error(), "requestID", req.ID)
		// Intentionally hide the error from the user
		err = errors.New(errorCode.String())
	case api.InvalidParamsError:
		h.lggr.Errorw("invalid params", "requestID", req.ID, "error", err.Error())
		err = errors.New("invalid params error: " + err.Error())
	case api.UnsupportedMethodError:
		h.lggr.Errorw("unsupported method", "requestID", req.ID, "method", req.Method, "error", err.Error())
		err = errors.New("unsupported method(" + req.Method + "): " + err.Error())
	case api.UserMessageParseError:
		h.lggr.Errorw("user message parse error", "requestID", req.ID, "error", err.Error())
		err = errors.New("user message parse error: " + err.Error())
	case api.NoError:
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
