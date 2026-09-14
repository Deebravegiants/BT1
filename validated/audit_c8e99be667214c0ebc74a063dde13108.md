### Title
Vault Gateway Handler Logs Full JSON-RPC Request (Including Plaintext JWT Auth Token) at Debug Level - (File: core/capabilities/vault/gw_handler.go)

### Summary
`GatewayHandler.HandleGatewayMessage` logs the entire incoming `jsonrpc.Request[json.RawMessage]` object — including its `Auth` field, which carries the caller-supplied bearer JWT used for JWT-based Vault authentication — at `Debug` level before any authorization or redaction occurs. [1](#0-0) 

### Finding Description
Every Vault request forwarded through the gateway to a node carries an `Auth` field populated with a caller-supplied JWT bearer token that the node uses to authenticate the request via `jwtBasedAuth.AuthorizeRequest`. [2](#0-1) 
This token is a first-class credential: it is minted per-request, bound to a request digest, and used by `authorizer.AuthorizeRequest` to establish the caller's authorized owner/org identity. [3](#0-2) 

Before any of that authorization logic runs, `HandleGatewayMessage` unconditionally logs the raw request object at Debug level:
```go
reqLggr := h.requestLogger(req, gatewayID)
reqLggr.Debugw("received message from gateway", "req", req)
``` [1](#0-0) 
Because `req` is passed as a structured field (not a redacted subset), the logger serializes the full struct, including the `Auth` string field carrying the plaintext JWT, to whatever debug log sink is configured (which may be a persistent local log file, per the node's `Log.File` config seen elsewhere in the codebase). [4](#0-3) 

Notably, the codebase already recognizes this class of bug and has added targeted protection elsewhere in the same package: `TestVaultHandler_InvalidParamsDoesNotLogRawParams` explicitly asserts that raw request params must never be logged in the gateway-side `handler.go` invalid-params path. [5](#0-4) 
However, that protection does not cover the *node-side* `GatewayHandler.HandleGatewayMessage` entry point, which still logs the full request object — including the `Auth` token — unconditionally at Debug on every message it receives from the gateway.

### Impact Explanation
This is the same bug class as CVE-2026-13750: sensitive authentication credentials are written into local, potentially persistent, debug log files. Any unprivileged actor able to submit a Vault-related JSON-RPC request through the gateway (e.g., `vault.secrets.create`, `vault.secrets.update`, `vault.secrets.delete`, `vault.secrets.list`) causes their own signed JWT bearer token to be written into the node operator's debug logs in plaintext. If a node operator enables Debug-level logging (a supported, documented configuration) and an attacker with local read access to those log files, or to any log aggregation pipeline the operator forwards debug logs to, obtains a copy, the attacker gains a valid, digest-bound JWT that authenticates the original caller's Vault request. This is a direct credential-disclosure vector consistent with the "Impact Explanation" bar of concrete key/secret disclosure and potential request impersonation.

### Likelihood Explanation
Reaching this log statement requires no privilege beyond being able to send a JSON-RPC message to the gateway that gets routed to the Vault `GatewayHandler` — i.e., any unprivileged, unauthenticated-at-this-point client request. The log line executes unconditionally on every inbound gateway message, prior to any authorization check, so it is triggered on the normal/expected request path, not an edge case. The only prerequisite for exploitation is that the node operator has Debug-level logging enabled (a common operational choice for troubleshooting) and that the attacker can access the resulting log file/stream.

### Recommendation
Redact or omit the `Auth` field (and any other credential-bearing fields) before logging the request object in `HandleGatewayMessage`, mirroring the redaction pattern already used in `handler_test.go`'s invalid-params logging guarantee — e.g., log `req.ID`, `req.Method`, and `hasAuth: req.Auth != ""` instead of the raw struct, consistent with how `authorizer.go` and `jwt_based_auth.go` already avoid logging the raw token (`"hasAuth", req.Auth != ""`). [6](#0-5) 

### Proof of Concept
1. Configure a Chainlink node with `Log.Level = 'debug'` and a `Log.File.Dir` set to a writable directory (a supported configuration, as validated by the node's own test fixtures).
2. As any unprivileged client, submit a Vault JSON-RPC request (e.g., `vault.secrets.list`) through the gateway with `req.Auth` set to a valid JWT bearer token.
3. On the node, `GatewayHandler.HandleGatewayMessage` executes `reqLggr.Debugw("received message from gateway", "req", req)` before authorization, writing the full request — including the plaintext JWT in `req.Auth` — to the node's debug log file.
4. An actor with read access to that log file (e.g., another local user, a misconfigured log-shipping pipeline, or a compromised monitoring agent) recovers the plaintext JWT and can replay it as the original caller against the still-valid digest/expiry window before the replay guard consumes it, or use it to correlate/deanonymize the original caller's authorized owner/org identity.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-182)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
```

**File:** core/capabilities/vault/jwt_based_auth.go (L187-192)
```go
// AuthorizeRequest verifies JWTBasedAuth state and token claims, and returns a common AuthResult.
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
```

**File:** core/capabilities/vault/authorizer.go (L99-119)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
	}
	if ownerErr := validateSecretOwnersMatchAuthorized(req, authResult.AuthorizedOwner()); ownerErr != nil {
		a.lggr.Errorw("owner binding rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "hasAuth", req.Auth != "", "error", ownerErr)
		return nil, ownerErr
	}
	a.lggr.Debugw("request authorized", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "")
	return authResult, nil
}
```

**File:** testdata/scripts/node/validate/disk-based-logging-no-dir.txtar (L9-22)
```text
-- config.toml --
Log.Level = 'debug'

[[EVM]]
ChainID = '1'

[[EVM.Nodes]]
Name = 'fake'
WSURL = 'wss://foo.bar/ws'
HTTPURL = 'https://foo.bar'

[Log.File]
MaxSize = '1.00mb'
Dir = ''
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
