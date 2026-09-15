### Title
JWT/Bearer auth token logged in plaintext when the Vault gateway handler receives a JSON-RPC message - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` logs the entire inbound `jsonrpc.Request[json.RawMessage]` object — including its `Auth` field, which carries the caller's raw JWT/bearer token — at Debug level before any authorization or redaction is applied.

### Finding Description
`HandleGatewayMessage` is the entry point that processes every JSON-RPC request relayed from the gateway to the Vault capability handler: [1](#0-0) 

The very first line, `reqLggr.Debugw("received message from gateway", "req", req)`, passes the whole `req` struct as a structured logging field. `req` is a `*jsonrpc.Request[json.RawMessage]`, the same type whose `Auth` field is referenced throughout the codebase to carry the caller's bearer token — e.g. it is explicitly stripped before re-marshalling requests in test helpers (`req.Auth = ""` in `outboundRequestWithoutAuth`) [2](#0-1) , and it is read directly for authentication in `AuthorizeRequest`: `v.validateToken(ctx, req.Auth)` [3](#0-2) .

Other call sites in the same package are careful not to log the raw token — `GatewayVaultRequestProcessor.authorizeAndStamp` deliberately logs only a boolean presence flag, `"hasAuth", req.Auth != ""`, instead of the token value [4](#0-3) . This shows the codebase is aware the `Auth` field is sensitive and normally redacts it — but `HandleGatewayMessage`'s `Debugw("received message from gateway", "req", req)` bypasses that discipline and serializes the struct (and its `Auth` field) wholesale into the log sink, since no `MarshalLogObject`/redaction wrapper for `jsonrpc.Request` was found in this repo's index.

This logging call executes unconditionally for every message reaching this handler, prior to `AuthorizeRequest`/JWT validation, so it fires for both legitimate and forged/expired tokens supplied by any unprivileged client that can reach the gateway's JSON-RPC vault endpoint.

### Impact Explanation
If Debug-level logging is enabled (a supported, non-privileged operational configuration, not a developer-only mode), every caller's JWT/session bearer token used to authenticate Vault secret operations (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`) is written to node logs in cleartext. Anyone with read access to those logs (log aggregation, monitoring, support tooling, or a lower-privileged operator) can extract a valid token and replay it to impersonate the original workflow owner/DAG-author-equivalent, matching the CVE's "act as another author" impact — here, acting as the Vault secret owner to create, update, delete, or enumerate that owner's secrets within the token's remaining validity window.

### Likelihood Explanation
Likelihood is moderate: it requires Debug logging enabled and log access, but the vulnerable log statement is on the hot path for every gateway-forwarded message with no additional preconditions, sampling, or gating — it is triggered by any unauthenticated request reaching the handler, before authorization succeeds or fails.

### Recommendation
Remove or redact the `Auth` field before logging the request in `HandleGatewayMessage` — log only non-sensitive fields (`req.Method`, `req.ID`) or an explicit `hasAuth` boolean, consistent with the pattern already used in `gateway_vault_request_processor.go`.

### Proof of Concept
1. Enable Debug-level logging on a Chainlink node running the Vault gateway handler.
2. As any client, send a JSON-RPC request (e.g. `secrets_list`) to the gateway with a `Bearer <JWT>` in the request's `Auth` field.
3. `GatewayHandler.HandleGatewayMessage` executes `reqLggr.Debugw("received message from gateway", "req", req)` before authorization completes.
4. Inspect node logs: the full raw JWT token appears in the `req` field of the "received message from gateway" log entry, in cleartext, independent of whether the token is later accepted or rejected.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-183)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

```

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1263-1266)
```go
func outboundRequestWithoutAuth(req jsonrpc.Request[json.RawMessage]) jsonrpc.Request[json.RawMessage] {
	req.Auth = ""
	return req
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L270-276)
```go
	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}
```
