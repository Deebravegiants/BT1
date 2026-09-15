This confirms the claim's core facts: `req.Auth` is the JWT/bearer credential field on `jsonrpc.Request[T]` used throughout the vault auth flow, and `HandleJSONRPCUserMessage` logs the full `req` struct at Debug level unconditionally before authorization occurs.Audit Report

## Title
Vault gateway handler logs the raw JWT/bearer `Auth` credential from every user request at Debug level - (File: core/services/gateway/handlers/vault/handler.go)

## Summary
`handler.HandleJSONRPCUserMessage` unconditionally logs the full incoming `jsonrpc.Request[json.RawMessage]` object — which includes the caller-supplied `Auth` field used as the JWT/bearer credential — at Debug level, before any authorization check runs. This mirrors the class of bug where sensitive credentials are written into server logs in plaintext, allowing anyone with log access (log aggregation, misconfigured shipping, support staff) to extract and replay a live token.

## Finding Description
The vulnerable log statement executes on every call to `HandleJSONRPCUserMessage`, gated only by ID validation, not by authorization: [1](#0-0) 

`req.Auth` is confirmed to be the JWT/bearer credential consumed throughout the vault authorization stack — `authorizer.authorizeRequest` branches on `req.Auth == ""` to select allowlist vs. JWT-based auth, and `jwtBasedAuth.AuthorizeRequest` calls `v.validateToken(ctx, req.Auth)` directly: [2](#0-1) [3](#0-2) 

Test helpers throughout the codebase further corroborate that `req.Auth` is the literal bearer token transmitted as `Authorization: Bearer <token>`, confirming it is a live, replayable credential, not a hash or derived value: [4](#0-3) 

Elsewhere in the same handler, once authorization fails, the code is careful to log only `req.Auth != ""` (a boolean) rather than the raw value: [5](#0-4) 
and the same discipline is used consistently in `authorizer.go` (`"hasAuth", req.Auth != ""`). This shows the codebase's authors are aware `Auth` is sensitive and deliberately avoid logging it raw in every other call site — except the one at line 403, which logs the entire `req` struct (including `Auth`) via structured logging with no field-level redaction. Because `jsonrpc.Request[T]` has no custom `MarshalLogObject`/redaction wired at this call site to strip `Auth`, the zap-based structured logger will serialize the struct including the raw `Auth` string when Debug-level logging is enabled.

The existing test `TestVaultHandler_InvalidParamsDoesNotLogRawParams` explicitly acknowledges this exact log line as a known gap: it observes logs starting at `InfoLevel` specifically "so the pre-existing whole-request Debug log is excluded," and only asserts that a later Error-level "invalid params" log doesn't leak the request params — it does not test or gate the line-403 Debug log at all: [6](#0-5) 

This confirms there is no existing test, redaction, or auth-gating that prevents the `Auth` credential from being logged at line 403.

## Impact Explanation
If Debug logging is enabled on a Gateway node — a standard, documented, supported operational mode, not an "operator misconfiguration" in the sense of exposing an otherwise-hidden vulnerability — every caller's JWT/bearer credential passed to the Vault capability is written to that node's logs in the clear, before authorization succeeds or fails. This is a credential/session disclosure that enables replay/impersonation of the original caller against the Vault DON, matching the "gateway request impersonation" / credential-disclosure impact category.

## Likelihood Explanation
The log statement executes unconditionally on every `HandleJSONRPCUserMessage` invocation — not gated by any error condition, and reachable by any unprivileged client sending a request to the vault gateway endpoint (`MethodSecretsCreate`, `MethodSecretsList`, etc.). The only precondition is that the operator has Debug-level logging enabled, which is a normal, supported node configuration rather than a privileged or unusual state, and does not require admin/host access from the attacker's perspective — the attacker only needs to send a normal request while logs are being collected/exposed downstream.

## Recommendation
Remove `"request", req` from the Debug log statement at line 403, or replace it with an explicit allowlist of non-sensitive fields (`method`, `requestID`) as already done a few lines later at line 437. If a redacted structured dump of the request is needed for debugging, implement a `MarshalLogObject`/copy-and-clear step that blanks `Auth` before logging, consistent with the `"hasAuth", req.Auth != ""` pattern used everywhere else in this codebase.

## Proof of Concept
1. Enable `Log.Level = 'debug'` on a Gateway node running the Vault handler.
2. Send any JSON-RPC vault request (e.g. `vault.secrets.list`) with a populated `Auth` JWT to the gateway.
3. Observe the node's Debug log entry `"handling vault request"` emitted at `core/services/gateway/handlers/vault/handler.go:403`; the serialized `request` field contains the caller's raw `Auth` token in plaintext.
4. As a Go unit test: call `h.HandleJSONRPCUserMessage(ctx, req, callback)` with `req.Auth = "test-jwt-token"` using `logger.TestObserved(t, zapcore.DebugLevel)`, then assert that no log entry's `ContextMap()` or serialized `request` field contains the string `"test-jwt-token"` — this test currently fails, proving the leak (extending the existing `TestVaultHandler_InvalidParamsDoesNotLogRawParams` pattern to cover the Debug-level line 403 call, which that test explicitly excludes).

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L394-403)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L426-434)
```go
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

**File:** core/capabilities/vault/jwt_based_auth.go (L188-193)
```go
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}
```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L547-559)
```go
func sendVaultSignedOCRRequestToGateway(t *testing.T, gatewayURL string, jsonRequest jsonrpc.Request[json.RawMessage], authorizedOwner string) jsonrpc.Response[vaulttypes.SignedOCRResponse] {
	t.Helper()

	authToken := jsonRequest.Auth
	jsonRequest = outboundRequestWithoutAuth(jsonRequest)

	requestBody, err := json.Marshal(jsonRequest)
	require.NoError(t, err, "failed to marshal vault request")

	headers := map[string]string{}
	if authToken != "" {
		headers["Authorization"] = "Bearer " + authToken
	}
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1023)
```go
func TestVaultHandler_InvalidParamsDoesNotLogRawParams(t *testing.T) {
	t.Parallel()

	// Observed at Info level so the pre-existing whole-request Debug log is excluded.
	lggr, logs := logger.TestObserved(t, zapcore.InfoLevel)
	h, callback, don, _ := setupHandlerWithLogger(t, lggr, limits.Factory{Settings: cresettings.DefaultGetter})
	// Don't expect SendToNode to be called for invalid params
	don.AssertNotCalled(t, "SendToNode")
```
