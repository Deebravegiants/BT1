Audit Report

## Title
Vault Gateway node handler logs full JSON-RPC request/response including the raw JWT bearer `Auth` token at Debug/Info level - (File: core/capabilities/vault/gw_handler.go)

## Summary
`GatewayHandler.HandleGatewayMessage` in the Vault capability's node-side gateway handler logs the entire inbound `*jsonrpc.Request[json.RawMessage]` object via `reqLggr.Debugw("received message from gateway", "req", req)` before authorization/redaction occurs. Since `jsonrpc.Request` carries an `Auth` field populated with the caller's JWT bearer token (used throughout `authorizer.go` and `jwt_based_auth.go` via `req.Auth`), this line writes the caller's raw JWT credential to node logs whenever Debug-level logging is enabled.

## Finding Description
The Vault gateway-facing handler receives `jsonrpc.Request[json.RawMessage]` objects forwarded from the Gateway, where the `Auth` field carries the caller-supplied JWT bearer token used for authorization, as confirmed by its use in `jwtBasedAuth.AuthorizeRequest` (`v.validateToken(ctx, req.Auth)`) [1](#0-0)  and in `authorizer.authorizeRequest`'s `if req.Auth == ""` branch selection logic [2](#0-1) .

In `HandleGatewayMessage`, the raw request — including this `Auth` field — is logged at Debug level before any authorization or field-level redaction takes place: [3](#0-2) . The response is separately logged at Info level after processing [4](#0-3) , though the response object (`*jsonrpc.Response[json.RawMessage]`) does not itself carry the `Auth` field, so that specific log line is not a credential leak.

Other logging call sites in the same package (`authorizer.go`, `jwt_based_auth.go`) demonstrate awareness of this risk, deliberately logging only `"hasAuth", req.Auth != ""` as a boolean rather than the raw token [5](#0-4) . This confirms the `Debugw("received message from gateway", "req", req)` call is inconsistent with the rest of the codebase's own redaction convention, and no sanitization is applied to `req` before it is logged.

A test in `core/services/gateway/handlers/vault/handler_test.go` explicitly references and works around "the pre-existing whole-request Debug log" [6](#0-5) , but that test file belongs to a **different package** — the Gateway-side (`core/services/gateway/handlers/vault`) handler, not the node-side `GatewayHandler` in `core/capabilities/vault/gw_handler.go` referenced by the claim's PoC. This is a package-name coincidence pointed at by the report, not direct proof that `gw_handler.go`'s Debug log is the one being worked around; the "pre-existing whole-request Debug log" being excluded in that test is more likely referring to a similar-but-separate Debug log inside the Gateway-side `handler.go`'s `HandleJSONRPCUserMessage`, not the node-side `HandleGatewayMessage` in the file the claim identifies.

Despite that citation mismatch, the core claim about `core/capabilities/vault/gw_handler.go` stands independently: line 182 does log the full `req` object, including `Auth`, at Debug level, with no redaction applied.

## Impact Explanation
The `Auth` field is the caller's JWT bearer token used to authorize vault secret operations (create/update/delete/list). Any party with read access to node debug logs can extract a live bearer token from `reqLggr.Debugw("received message from gateway", "req", req)` and replay it to impersonate the original requester's vault operations, subject to the token's remaining validity window and the replay-guard digest binding described in `authorizer.go`. This constitutes credential/secret exposure enabling request impersonation, falling under an in-scope Chainlink impact category (secret exfiltration / gateway request impersonation) — but only triggerable when Debug-level logging is enabled on the node, which is not the default production log level.

## Likelihood Explanation
Triggering the log line requires only sending a normal JWT-authenticated request through the Gateway to a node running the Vault capability — no malicious action needed, and the log statement fires unconditionally within `HandleGatewayMessage` on every message. However, the actual credential disclosure only manifests when the node's log level is set to Debug (not the response log at Info, which does not include `Auth` since `jsonrpc.Response` has no `Auth` field). This limits real-world exposure to nodes/operators who have Debug logging enabled, which is an operator-configuration factor rather than something purely under attacker control.

## Recommendation
Remove or redact the `Debugw("received message from gateway", "req", req)` call in `core/capabilities/vault/gw_handler.go`. Log structured, redacted fields only (method, request ID, gateway ID, `hasAuth` boolean, params/response size) — following the pattern already used in `authorizer.go` (`"hasAuth", req.Auth != ""`). If full-request debug logging is needed for troubleshooting, explicitly clear the `Auth` field on a copy of the request before logging it.

## Proof of Concept
1. Configure a node running the Vault capability with `LOG_LEVEL=debug`.
2. Send a JWT-authenticated `vault.secrets.list` (or create/update/delete) request through the Gateway to the node, with `Auth` set to a valid bearer JWT.
3. On the node, `GatewayHandler.HandleGatewayMessage` (`core/capabilities/vault/gw_handler.go:182`) executes `reqLggr.Debugw("received message from gateway", "req", req)` before authorization completes, writing the full `req` struct (including `Auth`) to the log stream.
4. Inspect the node's Debug-level log output; the JWT string appears in plaintext under the `"req"` field.
5. Replay the extracted JWT against the Gateway before it expires to perform vault operations as the original caller, subject to replay-guard digest checks in `authorizer.go`.

A concrete Go test to prove this: instantiate `GatewayHandler` with an observed test logger at `zapcore.DebugLevel`, call `HandleGatewayMessage` with a `req` containing a known `Auth` string, then assert the captured log entries contain that string.

### Citations

**File:** core/capabilities/vault/jwt_based_auth.go (L188-193)
```go
func (v *jwtBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	claims, err := v.validateToken(ctx, req.Auth)
	if err != nil {
		v.lggr.Debugw("JWTBasedAuth token validation failed", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("invalid JWT auth token: %w", err)
	}
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1021)
```go
func TestVaultHandler_InvalidParamsDoesNotLogRawParams(t *testing.T) {
	t.Parallel()

	// Observed at Info level so the pre-existing whole-request Debug log is excluded.
	lggr, logs := logger.TestObserved(t, zapcore.InfoLevel)
	h, callback, don, _ := setupHandlerWithLogger(t, lggr, limits.Factory{Settings: cresettings.DefaultGetter})
```
