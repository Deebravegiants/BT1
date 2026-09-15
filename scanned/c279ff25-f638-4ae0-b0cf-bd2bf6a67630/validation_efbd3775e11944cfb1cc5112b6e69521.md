### Title
Vault Gateway node handler logs full JSON-RPC request/response including the raw JWT bearer `Auth` token at Debug/Info level - (File: core/capabilities/vault/gw_handler.go)

### Summary
`GatewayHandler.HandleGatewayMessage` in the Vault capability's gateway-facing handler logs the entire inbound `jsonrpc.Request[json.RawMessage]` object (and the outbound response) to the node logger, without redacting the `Auth` field that carries the caller-supplied JWT bearer token used to authenticate/authorize the vault request. This mirrors the reported bug class: an unprivileged client's authentication credential is written verbatim into node logs by a debug/info log statement in the request-handling path.

### Finding Description
The Vault capability accepts requests forwarded from the internet-facing Gateway. Each request is a `jsonrpc.Request[json.RawMessage]` that carries an `Auth` field populated with the caller's JWT bearer token, as used throughout the authorization code: [1](#0-0) [2](#0-1) 

In `HandleGatewayMessage`, the raw request (including this `Auth` field) is logged before any authorization/redaction occurs, and the response is logged afterward: [3](#0-2) [4](#0-3) 

This is functionally identical to the reported bug class: logging an entire externally-supplied payload — including the caller's bearer credential — via a generic `Debugw`/`Infow`/`console.log`-style call, without field-level redaction. A test in the same package explicitly acknowledges this exists and works around it by asserting only at `Info` level to "exclude the pre-existing whole-request Debug log": [5](#0-4) 

Note that unlike `core/services/gateway/handlers/capabilities/v2/http_handler.go`, which logs only sizes (`requestBodySize`, `numHeaders`) rather than raw content, and unlike `core/web/router.go`'s `loggerFunc`, which runs the body through `readSanitizedJSON`/`redact` before logging, the Vault node-side gateway handler performs no such sanitization on the request object itself.

### Impact Explanation
The `Auth` field is the caller's JWT bearer token used to authorize vault operations (secrets create/update/delete/list). Anyone with read access to node logs (operators, log-aggregation pipelines, third-party managed-node providers, misconfigured log shipping) can extract a live bearer token and replay it to impersonate the original requester for vault operations, subject to the token's remaining validity window and any replay-guard digest binding. This is a credential/secret disclosure that enables request impersonation — the same class of impact as the reported GoCardless bearer-token logging issue, but here bound to the Vault capability's own authentication mechanism rather than an upstream banking API.

### Likelihood Explanation
Triggering this requires only sending a normal JWT-authenticated vault request to the Gateway/node — no malicious behavior is needed, and the log statements fire unconditionally on every gateway message received by this handler (Debug for the request, Info for the response). The response log at `Infow` level fires on every request in normal production configuration; the request log at `Debugw` fires whenever debug logging is enabled, which is common in troubleshooting and some managed deployments. Because the request test suite in this same package had to be written specifically to work around this log line, the maintainers are aware raw, unredacted request data (and therefore the `Auth` token) is emitted here.

### Recommendation
Stop logging the raw `*jsonrpc.Request`/`*jsonrpc.Response` objects wholesale. Log structured, redacted fields only (method, request ID, gateway ID, params/response size, `hasAuth` boolean) — following the pattern already used elsewhere in this same file/package (e.g., `authorizer.go`'s `"hasAuth", req.Auth != ""`). If full-body debug logging is required for troubleshooting, explicitly zero out or mask the `Auth` field before logging.

### Proof of Concept
1. A workflow/off-chain client sends a JWT-authenticated `vault.secrets.list` (or create/update/delete) request through the Gateway to a node running the Vault capability, with `Auth` set to a valid bearer JWT.
2. On the node, `GatewayHandler.HandleGatewayMessage` executes `reqLggr.Debugw("received message from gateway", "req", req)` before authorization completes, and `reqLggr.Infow("Sent message to gateway", "resp", response)` after processing.
3. With debug logging enabled (or by inspecting the info-level response log plus any downstream log line that still embeds the full struct), the node's log output contains the full `jsonrpc.Request` struct, including the `Auth` JWT string, in plaintext in the node's log stream / log aggregator.
4. An operator or anyone with log access extracts the JWT from the log line and can replay it against the Gateway to perform vault operations as the original caller until the token expires.

### Citations

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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1016-1024)
```go
func TestVaultHandler_InvalidParamsDoesNotLogRawParams(t *testing.T) {
	t.Parallel()

	// Observed at Info level so the pre-existing whole-request Debug log is excluded.
	lggr, logs := logger.TestObserved(t, zapcore.InfoLevel)
	h, callback, don, _ := setupHandlerWithLogger(t, lggr, limits.Factory{Settings: cresettings.DefaultGetter})
	// Don't expect SendToNode to be called for invalid params
	don.AssertNotCalled(t, "SendToNode")

```
