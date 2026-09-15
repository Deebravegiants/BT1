### Title
Vault Gateway Handler logs the full unvalidated JSON-RPC request — including the caller's JWT bearer auth token — to the node's Debug log - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` in the node-side Vault gateway handler logs the entire incoming JSON-RPC request object at Debug level before any authentication, signature, or schema validation has been performed: [1](#0-0) 

The `req` value is the full `jsonrpc.Request[json.RawMessage]` as forwarded by the gateway from an unprivileged, external client. For methods such as `MethodSecretsCreate`/`MethodSecretsUpdate`/`MethodSecretsDelete`/`MethodSecretsList`, that request carries the caller-supplied authentication material (JWT bearer token, as seen carried in the `Auth` field of outgoing requests throughout the vault test helpers, e.g. `jsonRequest.Auth` / `"Authorization": "Bearer " + authToken`) plus raw request params, before `h.requestProcessor.ProcessRequest` performs authorization: [2](#0-1) 

Serializing this struct into a structured log field writes the raw bearer/auth token (and any other sensitive request content) into the node's Debug-level system log, unredacted.

### Finding Description
This mirrors the bug class in CVE-2019-10364 (Jenkins EC2 plugin): sensitive credential material accepted from an untrusted caller is written into a persistent system log before validation, rather than being redacted or excluded from logging.

Notably, a sibling/newer Vault gateway-message handler (`core/services/gateway/handlers/vault`) explicitly guards against this exact failure mode: a dedicated regression test asserts that raw request params must never appear in logs, even at the point where params are rejected as invalid: [3](#0-2) 

That test's existence demonstrates the project's own security expectation — "raw params must not be logged" — which the `core/capabilities/vault/gw_handler.go` code path violates by logging the entire `req` (including its `Auth` field) unconditionally on every gateway message, prior to authorization.

### Impact Explanation
An unprivileged external client sending a Vault request through the gateway (secrets create/update/delete/list) causes its own JWT bearer token — a session credential used to authorize privileged Vault operations — to be written verbatim into the receiving node's Debug logs. Log files are commonly shipped to centralized logging/observability systems (e.g., beholder, which this package already imports) with broader read access than the Vault secrets pipeline itself, so this creates a path for credential disclosure to any party with node/log access, even though they were never authorized to see the caller's auth token. This satisfies "key/secret disclosure" and "cross-user response confusion" (any log reader can now impersonate/replay the leaked bearer token).

### Likelihood Explanation
Reachable directly by any unprivileged client issuing a normal Vault gateway request (no special privilege or race condition required) — the log line executes on every single inbound gateway message unconditionally, before authorization. The only gating factor is whether Debug-level logging is enabled in the deployment, which is a common operational/debugging configuration, not a hardened default in all environments.

### Recommendation
Stop logging the raw `req` object in `GatewayHandler.HandleGatewayMessage`. Log only non-sensitive correlation fields (request ID, method, gateway ID) as already done via `requestLogger`, and explicitly strip/redact the `Auth` field and raw `Params` before any logging, following the same discipline already implemented and tested in `core/services/gateway/handlers/vault/handler.go`/`handler_test.go`.

### Proof of Concept
1. An unprivileged client sends a `vault.secrets.create` (or update/delete/list) JSON-RPC request through the gateway HTTP endpoint with `Authorization: Bearer <token>`.
2. The gateway forwards the request to the node's `GatewayHandler.HandleGatewayMessage`.
3. Before any auth/signature validation, the handler executes `reqLggr.Debugw("received message from gateway", "req", req)`, serializing the full request — including the bearer token supplied in `req.Auth` — into the node's Debug log stream.
4. Anyone with read access to the node's logs (or to a downstream log aggregator) can extract the bearer token and reuse it to impersonate the original caller for subsequent Vault operations. [1](#0-0)

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-183)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

```

**File:** core/capabilities/vault/gw_handler.go (L186-211)
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1058)
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
```
