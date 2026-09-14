### Title
Unauthenticated gateway request logging exposes JSON-RPC params (including auth material) at Debug level - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go` logs the entire incoming JSON-RPC request object *before* authentication/authorization/validation occurs, at Debug level. This mirrors the CVE-2023-0436 bug class: sensitive request data (API/JWT-authenticated payloads, secrets-related params) is written to logs whenever DEBUG logging is enabled.

### Finding Description
`HandleGatewayMessage` immediately logs the raw request: [1](#0-0) 

```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
```

This happens for **every** method the handler serves — `MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, `MethodSecretsList`, `MethodPublicKeyGet` — before `requestProcessor.ProcessRequest` performs JWT/auth validation: [2](#0-1) 

Further down, several of the handler methods log the fully-unmarshalled request structure via `.String()` at Debug level as well, after "authorization": [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

Notably, the codebase already recognizes this exact bug class and has explicitly fixed/tested it in a **sibling** handler package, `core/services/gateway/handlers/vault/handler.go`, which has a regression test asserting raw params are never logged: [7](#0-6) 

That test (`TestVaultHandler_InvalidParamsDoesNotLogRawParams`) demonstrates the project's own security expectation: request params (which may carry secret material, request IDs correlated to sensitive marker data, or attacker-controlled fields) must not be logged verbatim. The `core/capabilities/vault/gw_handler.go` file, however, is a different implementation of essentially the same "vault gateway handler" concept and does not have the equivalent protection — it logs the raw `req` (whole JSON-RPC envelope including `Params`) unconditionally at Debug.

Unlike the sibling handler's Debug log of only correlation IDs (`requestID`, `method`, `gatewayID`), this one logs the entire request object (`"req", req`), which includes `req.Params` — the raw, attacker/user-supplied JSON payload for secret creation/update/deletion requests reaching the gateway from an unprivileged client.

### Impact Explanation
If the operator enables `Log.Level = 'debug'` (a supported, documented configuration option, see `core/config/docs/core.toml`), every vault-secrets-related gateway request payload is written to the node's logs. Because `CreateSecrets`/`UpdateSecrets` requests can carry encrypted secret blobs and identifying metadata, and other methods (`SecretsList`, `SecretsDelete`) carry raw request parameters and potential authorization details before validation, this creates a realistic risk of sensitive data disclosure to anyone with log access (log aggregation systems, support staff, disk access) — directly analogous to the MongoDB Atlas Operator's CVE-2023-0436 issue where GCP service account keys/API secrets were printed under DEBUG.

### Likelihood Explanation
Reachability requires only that the node operator has DEBUG logging enabled (not enabled by default, matching the CVE's "Required Configuration" note) and that an external/unprivileged caller sends a request to the gateway targeting the vault DON methods. No privileged access to the node itself is required to trigger the logging — only to enable debug mode, which is an operator action, matching the "operator must enable DEBUG" precondition of the original CVE. Because the vulnerable code path executes on every inbound gateway message regardless of authentication outcome, the trigger is trivially reachable by any unprivileged client capable of reaching the gateway's public endpoint.

### Recommendation
- Remove or redact the full request object from the initial `Debugw("received message from gateway", "req", req)` log line; log only correlation identifiers (`requestID`, `method`, `gatewayID`) as done in the sibling handler.
- Apply the same param-redaction discipline used in `core/services/gateway/handlers/vault/handler.go` (and validated by `TestVaultHandler_InvalidParamsDoesNotLogRawParams`) to `core/capabilities/vault/gw_handler.go`.
- Replace the later `.String()` logging of full `vaultCapRequest`/`r` objects with the addressable IDs only.
- Add a regression test analogous to `TestVaultHandler_InvalidParamsDoesNotLogRawParams` for `GatewayHandler.HandleGatewayMessage` to assert raw params never appear in logs, even at Debug level.

### Proof of Concept
1. Configure the node with `[Log] Level = 'debug'`.
2. Send a JSON-RPC request through the gateway targeting `vaulttypes.MethodSecretsCreate` (or `MethodSecretsUpdate`/`MethodSecretsList`/`MethodSecretsDelete`) with attacker-controlled or sensitive-looking data in `Params`.
3. Observe that `GatewayHandler.HandleGatewayMessage` logs the entire request (`"req", req`) at Debug level before authorization occurs — visible via `reqLggr.Debugw("received message from gateway", "req", req)` at `core/capabilities/vault/gw_handler.go:182`.
4. Subsequent `Debugw(...).String()` calls in `handleSecretsCreate`/`handleSecretsUpdate`/`handleSecretsDelete`/`handleSecretsList` re-log the parsed request structures again at Debug.

Note: I could not fully confirm within the available index whether `jsonrpc.Request[json.RawMessage]` carries additional auth/JWT material directly on the struct (e.g., a bearer token field) beyond `ID`/`Method`/`Params`, since the `jsonrpc` package definition itself was not retrievable via search. This affects only the precise severity of what auth-token exposure risk exists, not the core finding that raw, potentially-sensitive request `Params` are logged verbatim at Debug level.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-183)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

```

**File:** core/capabilities/vault/gw_handler.go (L187-211)
```go
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
```

**File:** core/capabilities/vault/gw_handler.go (L275-282)
```go
func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized create secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.CreateSecrets(ctx, &vaultCapRequest)
```

**File:** core/capabilities/vault/gw_handler.go (L294-301)
```go
func (h *GatewayHandler) handleSecretsUpdate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.UpdateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized update secrets request", "request", vaultCapRequest.String())
	vaultCapResponse, err := h.secretsService.UpdateSecrets(ctx, &vaultCapRequest)
```

**File:** core/capabilities/vault/gw_handler.go (L313-320)
```go
func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	h.lggr.Debugw("Processing authorized delete secrets request", "request", r.String())
	resp, err := h.secretsService.DeleteSecrets(ctx, r)
```

**File:** core/capabilities/vault/gw_handler.go (L338-346)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	r.Owner = authResult.AuthorizedOwner()

	h.lggr.Debugw("Processing authorized list secrets request", "request", r.String())
	resp, err := h.secretsService.ListSecretIdentifiers(ctx, r)
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1059)
```go
func TestVaultHandler_InvalidParamsDoesNotLogRawParams(t *testing.T) {
	t.Parallel()

	// Observed at Info level so the pre-existing whole-request Debug log is excluded.
	lggr, logs := logger.TestObserved(t, zapcore.InfoLevel)
	h, callback, don, _ := setupHandlerWithLogger(t, lggr, limits.Factory{Settings: cresettings.DefaultGetter})
	// Don't expect SendToNode to be called for invalid params
	don.AssertNotCalled(t, "SendToNode")

	const marker = "SENSITIVE_MARKER_123"
	invalidParams := json.RawMessage(`{"request_id":"req-1","injected":"` + marker + `"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "invalid-params-logs",
		Method: vaulttypes.MethodSecretsCreate,
		Params: &invalidParams,
	}

	// The invalid-params response is sent synchronously, so no goroutine is needed.
	err := h.HandleJSONRPCUserMessage(t.Context(), req, callback)
	require.NoError(t, err)

	resp, err := callback.Wait(t.Context())
	require.NoError(t, err)
	var secretsResponse jsonrpc.Response[vaultcommon.CreateSecretsResponse]
	require.NoError(t, json.Unmarshal(resp.RawResponse, &secretsResponse))
	assert.Equal(t, req.ID, secretsResponse.ID, "Request ID should match")
	assert.Equal(t, api.ToJSONRPCErrorCode(api.InvalidParamsError), secretsResponse.Error.Code, "Error code should match")

	invalidParamsLogs := logs.FilterMessage("invalid params")
	entries := invalidParamsLogs.All()
	require.Len(t, entries, 1, "expected exactly one 'invalid params' log entry")
	assert.Equal(t, zapcore.ErrorLevel, entries[0].Level)
	assert.Equal(t, req.ID, entries[0].ContextMap()["requestID"])
	assert.NotContains(t, entries[0].ContextMap(), "params", "raw params must not be logged")

	for _, e := range logs.All() {
		assert.NotContains(t, e.Message, marker)
		for k, v := range e.ContextMap() {
			if s, ok := v.(string); ok {
				assert.NotContains(t, s, marker, "log field %q must not contain raw request params", k)
			}
		}
	}
}
```
