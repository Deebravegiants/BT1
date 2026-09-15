The claim is confirmed by direct code inspection. The vulnerable line is exactly as cited:Audit Report

## Title
JWT/Bearer auth token logged in plaintext when the Vault gateway handler receives a JSON-RPC message - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` unconditionally logs the entire inbound `*jsonrpc.Request[json.RawMessage]` — including its `Auth` field, which carries the caller's raw bearer/JWT token — at Debug level before any authorization is performed. This is confirmed directly in the code: [1](#0-0) .

## Finding Description
`HandleGatewayMessage` is the entry point for every JSON-RPC message the gateway relays to the Vault node handler. Its very first action is `reqLggr.Debugw("received message from gateway", "req", req)`, passing the full `req` struct — a `*jsonrpc.Request[json.RawMessage]` — as a structured field before `h.requestProcessor.ProcessRequest` (which performs authorization) is invoked [2](#0-1) . Test code in the same repo confirms `jsonrpc.Request[json.RawMessage]` carries a raw bearer token in its `Auth` field (`req.Auth = "jwt-token"`) [3](#0-2) , and the same field is explicitly stripped before re-marshalling in test helpers (`req.Auth = ""`) precisely to avoid leaking it in request bodies/headers rather than the actual token [4](#0-3) . Elsewhere in the same package, `GatewayVaultRequestProcessor.authorizeAndStamp` deliberately avoids logging the token value, logging only `"hasAuth", req.Auth != ""` — demonstrating the codebase already treats `Auth` as sensitive and normally redacts it before logging [5](#0-4) . `HandleGatewayMessage`'s `Debugw` call bypasses this established redaction discipline by serializing the whole struct wholesale.

## Impact Explanation
When Debug-level logging is enabled — a supported node operational configuration — every caller's Vault-authenticating bearer token is written to node logs in cleartext for every message reaching this handler, regardless of whether the token is ultimately valid. Anyone with read access to node logs (log aggregation/monitoring/support tooling, or a lower-privileged operator) could extract a valid token and replay it to impersonate the token owner for Vault secret operations (create/update/delete/list), which maps to an in-scope "key/secret exfiltration" / gateway request impersonation impact.

## Likelihood Explanation
The log statement executes on every gateway-forwarded message unconditionally, with no additional gating, prior to authorization succeeding or failing, so it fires for any request reaching the handler once Debug logging is enabled. This is a real, reachable code path within the reviewed repo, not a hypothetical.

## Recommendation
Remove `req` from the Debug log line in `HandleGatewayMessage`, and instead log only non-sensitive fields (`req.Method`, `req.ID`, and a `"hasAuth", req.Auth != ""` boolean), consistent with the redaction pattern already used in `gateway_vault_request_processor.go`.

## Proof of Concept
1. Enable Debug-level logging on a node running the Vault gateway handler.
2. Send any JSON-RPC vault request (e.g., `secrets_list`) through the gateway with `Auth` set to a bearer/JWT token.
3. `GatewayHandler.HandleGatewayMessage` executes `reqLggr.Debugw("received message from gateway", "req", req)` at `core/capabilities/vault/gw_handler.go:182` before `ProcessRequest`/authorization runs.
4. Inspect node logs for the "received message from gateway" entry; the `req` field contains the full request struct including the raw `Auth` token value.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-206)
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
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
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

**File:** system-tests/tests/smoke/cre/vault_don_test_helpers.go (L1263-1266)
```go
func outboundRequestWithoutAuth(req jsonrpc.Request[json.RawMessage]) jsonrpc.Request[json.RawMessage] {
	req.Auth = ""
	return req
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
