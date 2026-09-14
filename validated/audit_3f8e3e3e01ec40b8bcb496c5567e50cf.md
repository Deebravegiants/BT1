Confirmed root-cause candidate: two on-node handlers log the entire `jsonrpc.Request[json.RawMessage]` object — which includes the `Auth` field carrying a bearer JWT / auth token — at `Debug`/`Info` level, unredacted, with no field-level scrubbing.

### Title
Full JSON-RPC request (including the `Auth` bearer token) is logged unredacted at Debug/Info level in the Vault gateway handlers - (File: `core/services/gateway/handlers/vault/handler.go`, `core/capabilities/vault/gw_handler.go`)

### Summary
`core/services/gateway/handlers/vault/handler.go:403` logs the whole incoming `jsonrpc.Request[json.RawMessage]` struct (`"request", req`) at Debug level before any authorization has happened, and `core/capabilities/vault/gw_handler.go:182` similarly logs `"req", req` at Debug and the full response at Info (`gw_handler.go:231`). The `Request` struct carries an `Auth` field populated directly from the client-supplied `Authorization: Bearer <token>` header (see `httpserver.go:227-234` and the JWT-auth tests using `req.Auth = token`). Unlike every other logging call site in this codebase (`authorizer.go`, `jwt_based_auth.go`, `gateway_vault_request_processor.go`), which deliberately log only `"hasAuth", req.Auth != ""` to avoid ever emitting the secret, these two call sites pass the entire request object to the structured logger, which will serialize `Auth` (the JWT bearer token used to authenticate/authorize the request) in plaintext to whatever debug/info-level log sink is configured. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Finding Description
This is the same bug class as CVE-2020-13881: a secret (there, a TACACS+ shared secret; here, a request-authenticating bearer token/JWT) is written to logs when a debug-level log setting is enabled, bypassing the application's own secret-redaction conventions. The rest of the vault authorization pipeline is careful about this — `authorizer.go` and `jwt_based_auth.go` consistently log only booleans (`"hasAuth", req.Auth != ""`) or derived claims, never the raw token, and there's an explicit regression test (`TestVaultHandler_InvalidParamsDoesNotLogRawParams` in `handler_test.go`) asserting that a different log line does not leak sensitive request content — but its own comment notes it deliberately excludes "the pre-existing whole-request Debug log", i.e. developers were aware this Debug log exists and left it out of scope rather than fixing it. [6](#0-5) 

Because `req.Auth` is populated straight from the unprivileged client's `Authorization` header on every inbound vault request (create/update/delete/list secrets, and the gateway relay path), any operator running the node/gateway with `Log.Level = 'debug'` will have every caller's raw JWT captured in the log stream. That JWT is the credential used to authorize secret create/update/delete/list operations for a specific `workflowOwner`/`orgID` (see `jwt_based_auth.go` validation flow), so its disclosure lets anyone with log access impersonate that caller — i.e. bypass the vault's authorization/replay-guard mechanism entirely by replaying (or forging with knowledge of) the captured token, exactly analogous to the pam_tacplus shared-secret leak enabling credential-based bypass.

### Impact Explanation
Disclosure of `req.Auth` allows an attacker with access to debug logs (log aggregation systems, journald, shipped logs, support bundles) to impersonate the legitimate caller and issue vault secret operations (`vault.secrets.create/update/delete/list`) on behalf of that workflow owner, since the authorization layer (`jwt_based_auth.go`) treats a valid token+matching digest as sufficient proof of identity. This is a credential/secret disclosure leading to authentication bypass and potential unauthorized secret manipulation, which is explicitly in-scope per the validation criteria (key/secret disclosure, request impersonation).

### Likelihood Explanation
Requires only that the node/gateway operator has `Log.Level` set to `debug` (a supported, documented configuration, not a misconfiguration outside normal operation — see the various `testdata/scripts/node/validate/*.txtar` fixtures that set `Log.Level = 'debug'` as a standard supported mode) and that an unprivileged client sends any vault request with a `Bearer` token. No special network position or privileged access is needed to trigger the log write — any external client hitting the gateway's public HTTP endpoint triggers it.

### Recommendation
Redact `Auth` before logging the request object in both locations: replace `"request", req` / `"req", req` with a redacted copy (e.g., set `req.Auth = ""` on a shallow copy before logging, or log `"hasAuth", req.Auth != ""` plus non-sensitive fields like `method`/`id`, mirroring the existing pattern already used in `authorizer.go` and `gateway_vault_request_processor.go`). Also review `reqLggr.Infow("Sent message to gateway", "resp", response)` for any response fields that might carry sensitive material.

### Proof of Concept
1. Configure a node/gateway with `Log.Level = 'debug'`.
2. As an unprivileged client, send a `vault.secrets.list` (or create/update/delete) JSON-RPC request to the gateway HTTP endpoint with `Authorization: Bearer <JWT>`.
3. Observe the node's debug log output for `"handling vault request"` (from `core/services/gateway/handlers/vault/handler.go:403`) or `"received message from gateway"` (from `core/capabilities/vault/gw_handler.go:182`) — the serialized `req` object contains the full `Auth` value, i.e., the raw bearer JWT, in cleartext in the log line.
4. An attacker who obtains this log line can reuse the JWT (subject to its expiry and replay-guard state) to authenticate as that caller for vault operations.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-404)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
	if req.Method == vaulttypes.MethodPublicKeyGet {
```

**File:** core/capabilities/vault/gw_handler.go (L180-182)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)
```

**File:** core/capabilities/vault/gw_handler.go (L226-231)
```go
	if err = h.gatewayConnector.SendToGateway(ctx, gatewayID, response); err != nil {
		reqLggr.Errorw("Failed to send message to gateway", "error", err)
		return err
	}

	reqLggr.Infow("Sent message to gateway", "resp", response)
```

**File:** core/capabilities/vault/authorizer.go (L99-118)
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
```

**File:** core/services/gateway/network/httpserver.go (L226-234)
```go
	// Optionally extract jwt token from authorization header
	authHeader := r.Header.Get("Authorization")
	jwtToken := ""
	if authHeader != "" {
		jwtToken = strings.TrimPrefix(authHeader, "Bearer ")
	}

	startTime := time.Now()
	rawResponse, httpStatusCode := s.handler.ProcessRequest(r.Context(), rawMessage, jwtToken)
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1050)
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

```
