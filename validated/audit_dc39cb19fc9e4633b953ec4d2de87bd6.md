### Title
Nil pointer dereference (DoS) in Vault gateway handler when `PublicKeyGet` request arrives with `nil` params - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go` dispatches `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet` without any nil-check on `req.Params`, unlike the `SecretsCreate`/`SecretsUpdate`/`SecretsDelete`/`SecretsList` methods, which are gated behind `GatewayVaultRequestProcessor.ProcessRequest` (which explicitly rejects `req.Params == nil` in `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest`, see `core/capabilities/vault/gateway_vault_request_processor.go:114-232`).

### Finding Description
In `core/capabilities/vault/gw_handler.go`: [1](#0-0) 

For `MethodPublicKeyGet`, the code calls `h.handlePublicKeyGet(ctx, gatewayID, req)` directly with no pre-validation, whereas the other four methods run through `h.requestProcessor.ProcessRequest`, which validates `req.Params != nil` before proceeding.

`handlePublicKeyGet` then unconditionally dereferences `req.Params`: [2](#0-1) 

If `req.Params` is `nil`, `json.Unmarshal(*req.Params, r)` dereferences a nil `*json.RawMessage`, causing a Go runtime nil pointer dereference panic. Unlike the other four vault methods (which explicitly check `req.Params == nil` in `gateway_vault_request_processor.go`), no such guard exists on this path, so a malformed `vault.publicKey.get` request (JSON-RPC request with the method set but `"params"` omitted or `null`) reaches `handlePublicKeyGet` and panics.

This mirrors the CVE-2019-15680 bug class: a null/missing input field is dereferenced without a nil check, causing denial of service via unhandled panic, in a request-parsing routine reachable over the network.

### Impact Explanation
`GatewayHandler` runs inside the node process and handles requests forwarded from the gateway (`HandleGatewayMessage` is invoked from the node's gateway connector read loop, `core/services/gateway/connector/connector.go:277-296`). If a panic is not recovered somewhere higher in that call chain (e.g., in the connector's read loop or the goroutine driving `HandleGatewayMessage`), it will crash the node process, denying vault/secrets service to all workflows on that node — a Denial of Service. Even if recovered by a higher-level goroutine wrapper, this at minimum aborts in-flight request handling for the vault gateway handler until restarted.

### Likelihood Explanation
I was not able to fully confirm, within available search results, whether the internet-facing Gateway (`core/services/gateway/handlers/vault/handler.go`, the *gateway-side* handler that receives HTTP requests from users at `core/services/gateway/gateway.go:ProcessRequest`) validates `req.Params` for `MethodPublicKeyGet` before forwarding the request on to nodes. If the gateway-side handler forwards user-supplied JSON-RPC requests to nodes largely as-is (which is architecturally consistent with `ProcessRequest`'s generic JSON-RPC request decoding and dispatch shown in `core/services/gateway/gateway.go:221-295`), then an unprivileged external caller sending a `vault.publicKey.get` request with `"params": null` or omitted `"params"` could directly trigger this node-side panic. This is a plausible but not fully proven reachability chain from an unauthenticated HTTP client through the gateway to the node handler — confirming it exactly requires reading `core/services/gateway/handlers/vault/handler.go`'s full request-forwarding logic, which I could not completely retrieve.

### Recommendation
Add the same nil-params guard used elsewhere in this file/package to `handlePublicKeyGet`, e.g.:
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
    if req.Params == nil {
        return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))
    }
    r := &vaultcommon.GetPublicKeyRequest{}
    if err := json.Unmarshal(*req.Params, r); err != nil {
        ...
```
Additionally, audit all `json.Unmarshal(*req.Params, ...)` call sites across the gateway/vault/confidentialrelay handlers to ensure a consistent nil-check policy, and consider adding panic-recovery around per-message handler invocation in the gateway connector's read loop as defense-in-depth.

### Proof of Concept
1. As an unprivileged caller (or a compromised/faulty gateway relay), send a JSON-RPC request to the vault gateway handler with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
   (i.e., `"params"` field omitted or explicitly `null`).
2. This reaches `GatewayHandler.HandleGatewayMessage` → `case vaulttypes.MethodPublicKeyGet: response = h.handlePublicKeyGet(ctx, gatewayID, req)` with `req.Params == nil`.
3. `handlePublicKeyGet` executes `json.Unmarshal(*req.Params, r)`, dereferencing the nil `*json.RawMessage`, causing a runtime panic (nil pointer dereference), crashing the goroutine/handler (and potentially the node process if unrecovered).

**Caveat:** I could not fully verify, due to index/search limitations, whether the gateway-side HTTP-facing handler performs its own nil-params validation before relaying to the node for this specific method, which is the piece needed to fully confirm end-to-end reachability from an unauthenticated network client. If a background Devin session can access the complete `core/services/gateway/handlers/vault/handler.go` file, this should be checked to close out full proof of the trust boundary crossing.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L187-211)
```go
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
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/capabilities/vault/gw_handler.go (L364-373)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	resp, err := h.secretsService.GetPublicKey(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to get public key: %w", err))
	}
```
