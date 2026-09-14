### Title
Vault gateway handlers log the full JSON-RPC request — including the authentication credential (`req.Auth`) — at Debug level before authorization - ([File: core/services/gateway/handlers/vault/handler.go], [File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault capability's gateway-side and node-side message handlers log the entire inbound `jsonrpc.Request[json.RawMessage]` object — which carries the caller-supplied `Auth` field (the JWT bearer credential used for per-request authorization) — via `Debugw` before the request has been authorized or validated. This mirrors the FusionPBX CVE-2019-11407 bug class: excessive debug output that discloses authentication material to anyone who can read the debug logs, triggered simply by an unprivileged client sending a request.

### Finding Description
Two entry points reachable from any unprivileged client hitting the gateway log the raw request object prior to (or independent of) authorization:

- `core/services/gateway/handlers/vault/handler.go` `HandleJSONRPCUserMessage`: `h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)` [1](#0-0) , executed before the request has been authorized by `h.requestProcessor.ProcessRequest` [2](#0-1) .
- `core/capabilities/vault/gw_handler.go` `HandleGatewayMessage`: `reqLggr.Debugw("received message from gateway", "req", req)` [3](#0-2) , also logged before the switch that performs authorization via `h.requestProcessor.ProcessRequest`.

The `req` value being logged is a `jsonrpc.Request[json.RawMessage]` that carries an `Auth` field used throughout the authorization path — e.g. `authorizer.go` checks `req.Auth != ""` to decide between allowlist-based and JWT-based authorization [4](#0-3) , and logs elsewhere deliberately avoid printing the raw value and only log `"hasAuth", req.Auth != ""` as a boolean flag [5](#0-4) . This shows the team is aware that the `Auth` value is sensitive and should not be dumped raw — yet the two handler entry points above pass the entire `req` struct (which contains that same `Auth` field plus raw `Params`) directly into `Debugw`, bypassing that redaction discipline.

Separately, the project explicitly tests that invalid-params responses do NOT leak raw request params into logs (`TestVaultHandler_InvalidParamsDoesNotLogRawParams`) [6](#0-5) , confirming an established security expectation that raw request content (including credentials) must not appear in logs — but that guard only covers the "invalid params" error message, not the unconditional "handling vault request"/"received message from gateway" Debug lines that run on every single inbound message.

### Impact Explanation
If Debug-level logging is enabled on a node (an operator-configurable, non-privileged-user setting; `Log.Level = 'debug'` is a supported, documented configuration [7](#0-6) ), every JWT-authenticated Vault request (secrets create/update/delete/list) sent to that node's gateway/Vault capability results in the caller's bearer JWT and raw secret-related request payload being written into node logs. Anyone with access to those logs (log aggregation, shipped audit/log files, etc.) can recover a valid JWT for the request's validity window and potentially replay or analyze it, or correlate raw secret identifiers/owners. This is a credential/secret disclosure issue matching the CVE-2019-11407 bug class (excessive debug information disclosing credentials), reachable purely by an unprivileged client sending a normal request — no privileged access or malicious peer/node required.

### Likelihood Explanation
Reaching the vulnerable log lines requires no special privilege: any client capable of sending a JSON-RPC message to the gateway (which is the intended entry point for workflow owners/unprivileged Vault users) triggers both log statements unconditionally, before any authorization check succeeds or fails. The only precondition is that the node has Debug logging enabled, which is a common operational choice for troubleshooting and is explicitly documented as a supported level. Given the codebase's own test coverage shows the team specifically hardening against raw-param leakage elsewhere, this indicates the two full-`req` debug logs were most likely overlooked rather than intentionally accepted.

### Recommendation
- Remove or redact the `req`/`request` field from the `Debugw` calls in `HandleJSONRPCUserMessage` (`core/services/gateway/handlers/vault/handler.go:403`) and `HandleGatewayMessage` (`core/capabilities/vault/gw_handler.go:182`).
- Replace with a redacted summary, mirroring the pattern already used in `authorizer.go` (`"hasAuth", req.Auth != ""`), and avoid embedding `req.Params` raw JSON in logs.
- Extend the existing `TestVaultHandler_InvalidParamsDoesNotLogRawParams`-style assertions to cover the unconditional entry-point debug logs, not just the invalid-params error path.

### Proof of Concept
1. Configure a node with `Log.Level = 'debug'`.
2. As an unprivileged client, send any valid JWT-authenticated request to the gateway for a Vault method (e.g., `secrets_list`), including the `Auth` JWT field.
3. Observe the node's debug logs contain the line `"received message from gateway" req=<full request including Auth JWT>` (`core/capabilities/vault/gw_handler.go:182`) and/or `"handling vault request" ... request=<full request>` (`core/services/gateway/handlers/vault/handler.go:403`), exposing the raw JWT bearer token and request payload in plaintext logs.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L403-403)
```go
	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
```

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

**File:** core/capabilities/vault/gw_handler.go (L180-182)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
```

**File:** core/capabilities/vault/authorizer.go (L106-117)
```go
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
```

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}
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

**File:** core/config/docs/core.toml (L140-151)
```text
[Log]
# Level determines only what is printed on the screen/console. This configuration does not apply to the logs that are recorded in a file (see [`Log.File`](#logfile) for more details).
#
# The available levels are:
#  - "debug": Useful for forensic debugging of issues.
#  - "info": High-level informational messages. (default)
#  - "warn": A mild error occurred that might require non-urgent action. Check these warnings semi-regularly to see if any of them require attention. These warnings usually happen due to factors outside of the control of the node operator. Examples: Unexpected responses from a remote API or misleading networking errors.
#  - "error": An unexpected error occurred during the regular operation of a well-maintained node. Node operators might need to take action to remedy this error. Check these regularly to see if any of them require attention. Examples: Use of deprecated configuration options or incorrectly configured settings that cause a job to fail.
#  - "crit": A critical error occurred. The node might be unable to function. Node operators should take immediate action to fix these errors. Examples: The node could not boot because a network socket could not be opened or the database became inaccessible.
#  - "panic": An exceptional error occurred that could not be handled. If the node is unresponsive, node operators should try to restart their nodes and notify the Chainlink team of a potential bug.
#  - "fatal": The node encountered an unrecoverable problem and had to exit.
Level = 'info' # Default
```
