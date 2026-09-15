Based on my investigation, I found a strong analog: `core/capabilities/vault/gw_handler.go`'s `HandleGatewayMessage` unconditionally logs the entire incoming `jsonrpc.Request[json.RawMessage]` — including the `Auth` field, which carries the raw client-supplied JWT bearer token — at Debug level, **before** any authentication/authorization check runs.

### Title
Vault Gateway Handler Logs Raw JWT Bearer Token Regardless of Authentication Outcome - (File: core/capabilities/vault/gw_handler.go)

### Summary
`GatewayHandler.HandleGatewayMessage` logs the full incoming vault request object (`"req", req`) at Debug level immediately upon receipt, prior to calling `h.requestProcessor.ProcessRequest` (which performs JWT/allowlist authorization). Because `jsonrpc.Request[json.RawMessage]` carries an `Auth` field populated with the caller's raw JWT bearer token (as shown throughout `core/capabilities/vault/authorizer_test.go` and `jwt_based_auth_test.go`, e.g. `req.Auth = token`), this log statement persists the client's authentication credential to node logs for every request — successful, malformed, or outright rejected by auth.

### Finding Description
The request path is: an external client sends a `vault.secrets.create/update/delete/list` request to the public gateway HTTP endpoint (`core/services/gateway/network/httpserver.go`'s `handleRequest`, which extracts the bearer token into `jwtToken` and calls `ProcessRequest`), the gateway relays it node-side via `SendToNode`, and each vault-capability DON node receives it in `GatewayHandler.HandleGatewayMessage`: [1](#0-0) 

The log call `reqLggr.Debugw("received message from gateway", "req", req)` occurs unconditionally at the top of the handler, before the switch statement that dispatches to `h.requestProcessor.ProcessRequest`, which is where JWT validation (`authorizer.go`'s `AuthorizeRequest` / `jwt_based_auth.go`'s `AuthorizeRequest`) actually happens: [2](#0-1) 

The `Auth` field on `jsonrpc.Request` is the raw bearer token string, confirmed by test usage such as `req.Auth = "jwt-token"` and `req.Auth = token` in [3](#0-2)  and [4](#0-3) . Since the whole struct is passed to zap's structured logger via `%v`-style field encoding without redaction, an invalid, expired, or entirely fabricated JWT is logged in full regardless of whether authorization later succeeds or fails — mirroring the reported n8n-mcp pattern of logging `Authorization`-derived credentials from rejected requests.

Notably, the codebase already treats this exact bug class as sensitive elsewhere: a dedicated regression test, `TestVaultHandler_InvalidParamsDoesNotLogRawParams`, asserts that raw request params/markers must never appear in logs at the gateway-side handler in `core/services/gateway/handlers/vault/handler.go`: [5](#0-4) 
No equivalent guard exists for the node-side `GatewayHandler.HandleGatewayMessage`'s whole-request Debug log, which additionally includes the `Auth` bearer token (a field the params-focused test doesn't cover).

### Impact Explanation
If Debug-level logging is enabled on a vault-capability node (a supported, documented log level, not a debug-only build), every vault request's JWT bearer token is written to node logs — including tokens from requests that fail JWT validation, replay checks, or owner-binding checks, i.e., requests from unauthenticated or malicious actors. In deployments where logs are aggregated, forwarded to SIEM, or accessible to operators/support outside the strict trust boundary of the vault DON, this discloses valid or near-valid OAuth-scoped JWTs (`vault.secrets.create/update/delete/list` scopes tied to a workflow owner/org), enabling replay or misuse of that credential to impersonate the workflow owner for vault secret operations — matching CWE-532 and the CVSS vector's confidentiality impact.

### Likelihood Explanation
Exploitation requires only sending a request (even malformed or unauthorized) to the public gateway path that reaches a vault-capability node's `HandleGatewayMessage`, and requires the node operator to have Debug logging enabled (a common non-default-but-supported configuration for diagnostics). No authentication bypass is needed to trigger the log write; the write happens unconditionally at receipt.

### Recommendation
Remove or redact the `Auth` field before logging the request object in `GatewayHandler.HandleGatewayMessage`, mirroring the pattern already used elsewhere in the codebase (`"hasAuth", req.Auth != ""` in `authorizer.go` and `gateway_vault_request_processor.go`) instead of logging the raw struct. Add a similar redaction test to `gw_handler_test.go` as exists for `handler_test.go`'s `TestVaultHandler_InvalidParamsDoesNotLogRawParams`.

### Proof of Concept
1. Configure a vault-capability node with Debug-level logging enabled.
2. Send any `vault.secrets.create` (or update/delete/list) JSON-RPC request through the public gateway HTTP endpoint with a fabricated/expired `Authorization: Bearer <token>` header — the request need not pass authorization.
3. The gateway relays the message to the node; `GatewayHandler.HandleGatewayMessage` executes `reqLggr.Debugw("received message from gateway", "req", req)` before authorization runs, writing the full request — including the raw bearer token in `req.Auth` — to the node's logs.
4. Inspect node logs (or any log aggregation/SIEM pipeline consuming them) to observe the disclosed bearer token, regardless of the subsequent 401/auth-failure outcome.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-199)
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
```

**File:** core/capabilities/vault/jwt_based_auth.go (L187-193)
```go
// AuthorizeRequest verifies JWTBasedAuth state and token claims, and returns a common AuthResult.
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}
```

**File:** core/capabilities/vault/authorizer_test.go (L29-34)
```go
	authResult, err := a.AuthorizeRequest(t.Context(), jsonrpc.Request[json.RawMessage]{
		ID:     "1",
		Method: vaulttypes.MethodSecretsCreate,
		Params: (*json.RawMessage)(&params),
		Auth:   "jwt-token",
	})
```

**File:** system-tests/lib/cre/vault/jwt_auth_test.go (L70-70)
```go
	req.Auth = token
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
