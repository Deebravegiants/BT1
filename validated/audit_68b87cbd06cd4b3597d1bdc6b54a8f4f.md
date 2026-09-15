Audit Report

## Title
Vault gateway handler logs the raw JWT bearer token (`req.Auth`) in plain text on every incoming request - (File: `core/services/gateway/handlers/vault/handler.go`)

## Summary
`HandleJSONRPCUserMessage` in the vault gateway handler unconditionally logs the entire incoming `jsonrpc.Request[json.RawMessage]` object via `h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)` before any authentication or authorization check runs. Because `req.Auth` carries the caller-supplied JWT that authenticates the vault request (confirmed by `req.Auth = mustMintVaultJWTForRequest(...)` and `headers["Authorization"] = "Bearer " + authToken` usage throughout the test helpers), this line writes the raw bearer token to node logs whenever `Log.Level = 'debug'` is enabled.

## Finding Description
`HandleJSONRPCUserMessage` logs `req` in full at line 403, prior to the `req.Method == vaulttypes.MethodPublicKeyGet` branch and prior to `h.requestProcessor.ProcessRequest` (the authorization step) at line 427: [1](#0-0) 

`req` is a `jsonrpc.Request[json.RawMessage]` whose `Auth` field is the JWT credential used to authenticate the request. This is confirmed by usage across the codebase where `req.Auth` is populated with a signed JWT and treated as the primary credential validated by `jwtBasedAuth.AuthorizeRequest`: [2](#0-1) [3](#0-2) 

Elsewhere in the same authorizer code, the token itself is deliberately never logged — only its presence (`"hasAuth", req.Auth != ""`) is recorded — showing the codebase is aware `Auth` is sensitive and normally redacts it: [4](#0-3) [5](#0-4) 

The `TestVaultHandler_InvalidParamsDoesNotLogRawParams` test further confirms that raw request material is treated as sensitive and explicitly tested against leaking into logs, but that test only covers `params`, not `Auth`: [6](#0-5) 

The line at 403 breaks this established pattern by passing the full `req` struct (including `Auth`) directly to `Debugw`, which relies on zap's default reflection-based encoding of struct fields — there is no evidence in the codebase of a custom `MarshalLogObject`/redaction on the `jsonrpc.Request` type (defined in the external `chainlink-common` module) that would strip `Auth` before serialization.

## Impact Explanation
This is a credential/secret exposure through logs (in-scope impact category: key/secret exfiltration). Anyone with read access to node logs when `Log.Level = 'debug'` is set can recover the raw JWT bearer token for any vault request, including its embedded claims (org ID, workflow owner, OAuth scopes). This is a genuine deviation from the codebase's own established discipline of redacting `Auth`/secrets from logs elsewhere.

## Likelihood Explanation
The log line executes unconditionally for every vault gateway request when the operator has enabled Debug-level logging, which is a documented, non-exotic configuration option. No attacker action is needed beyond obtaining log access, but note the log line itself is only reachable by an unprivileged client sending a request — it does not itself grant an unprivileged attacker access to the logs; log access requires separate access to the node's log stream/aggregation (operator-facing, not directly exploitable by an internet-facing unprivileged client alone). This nuance limits — but does not eliminate — real-world exploitability, since the actual disclosure vector (reading node logs) is not itself achievable by an unprivileged remote client; it requires an additional party with log-reading access.

## Recommendation
Redact `req.Auth` before logging the request object in `HandleJSONRPCUserMessage`, e.g., construct a shallow copy with `Auth` cleared, or log only safe fields (`method`, `id`, `hasAuth`) consistent with the pattern already used in `core/capabilities/vault/authorizer.go` and the handler's own error path at line 432. Add a regression test analogous to `TestVaultHandler_InvalidParamsDoesNotLogRawParams` asserting the JWT value never appears in any log entry.

## Proof of Concept
1. Configure a node with `Log.Level = 'debug'`.
2. Send a vault JSON-RPC request (e.g., `vault.secrets.list`) to the gateway's vault endpoint with `Authorization: Bearer <jwt>` and `req.Auth = <jwt>` in the JSON body.
3. Inspect node logs for the `"handling vault request"` entry emitted by `core/services/gateway/handlers/vault/handler.go:403`; the `request` field will contain the full `jsonrpc.Request` struct including the `Auth` value in plaintext.
4. A Go unit test can mount a `zaptest`/`observer` logger core, invoke `HandleJSONRPCUserMessage` with a request containing a marker JWT string in `Auth`, and assert the marker never appears in any captured log entry — following the same pattern as `TestVaultHandler_InvalidParamsDoesNotLogRawParams`.

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

**File:** core/services/gateway/handlers/vault/handler.go (L432-432)
```go
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
```

**File:** core/capabilities/vault/authorizer.go (L106-106)
```go
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1044-1058)
```go
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
