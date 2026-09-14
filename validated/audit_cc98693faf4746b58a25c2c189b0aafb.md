### Title
Nil pointer dereference panic on Vault `PublicKeyGet` requests with missing `params` crashes the node-side gateway handler - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The node-side Vault `GatewayHandler` handles `vaulttypes.MethodPublicKeyGet` requests forwarded from the gateway by calling `handlePublicKeyGet`, which dereferences `*req.Params` without checking whether `req.Params` is nil, unlike every other handler method in the same file (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) and unlike the legacy message path (`ValidatedMessageFromReq`), which all explicitly guard against nil `Params`. This mirrors the CVE-2025-65563 bug class: a message missing a mandatory field is not validated before being dereferenced, causing a panic instead of a controlled error.

### Finding Description
On the node side, `GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet` without any pre-check of `req.Params`: [1](#0-0) 

```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
``` [2](#0-1) 

`json.Unmarshal(*req.Params, r)` dereferences `req.Params` (a `*json.RawMessage`) without a nil check. Every other handler function in this file (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) has the exact same dereference pattern, so all of them are equally vulnerable, but `PublicKeyGet` is the one that requires no authorization and is easiest to reach: [3](#0-2) [4](#0-3) 

On the gateway side, `handler.HandleJSONRPCUserMessage` treats `MethodPublicKeyGet` as not requiring authorization and, on a cache miss, forwards the caller's raw request (including a possibly-nil `Params`) unchanged to every DON node via `fanOutToVaultNodes` → `don.SendToNode`, with no `Params` validation performed anywhere in that path: [5](#0-4) [6](#0-5) [7](#0-6) 

Because the gateway-side handler never unmarshal-checks `Params` for this method (it only needs it once cached, via `handlePublicKeyGetSynchronously`, which also never touches `req.Params`), a request with `Params: nil` (or omitted) sails straight through to every node in the DON, where the node's `GatewayHandler.handlePublicKeyGet` panics on `*req.Params`.

### Impact Explanation
A crash in the Vault gateway connector handler goroutine caused by an unhandled nil-pointer panic can take down the node process (or at minimum the connector's message-processing goroutine, depending on whether a top-level recover exists in that call chain — this was not confirmed in the available code and would need verification in a live/test run). Because `PublicKeyGet` requires no authorization, this is triggerable by any unauthenticated actor able to reach the gateway HTTP/JSON-RPC endpoint for the Vault handler, and a single malicious message is fanned out to every member node of the DON simultaneously, amplifying the denial-of-service impact to the whole Vault DON rather than a single node.

### Likelihood Explanation
High. `PublicKeyGet` is explicitly designed as an unauthenticated, pre-auth path (`"Public key requests don't require authorization"`), so no allowlist/JWT bypass is needed. The only condition needed is a cache miss on the gateway (`h.getCachedPublicKey()` returning nil), which is guaranteed to be true at least on gateway/node startup or after cache invalidation, and can be forced by any client whose request arrives before the periodic key refresh populates the cache.

### Recommendation
Add an explicit `req.Params == nil` check in `GatewayHandler.handlePublicKeyGet` (and for consistency in the other `handleSecrets*` functions in `core/capabilities/vault/gw_handler.go`) before dereferencing `req.Params`, returning a `UserMessageParseError`/`InvalidParamsError` response instead of panicking — matching the pattern already used in `ValidatedMessageFromReq` (`core/services/gateway/handlers/common/message_util.go:43-45`) and in `authorizer.go`'s `validateSecretOwnersMatchAuthorized`.

### Proof of Concept
1. As an unauthenticated client, send a Vault JSON-RPC request to the gateway with method `vault.publicKey.get` and `"params"` omitted (or explicitly `null`), before the gateway's public-key cache has been populated (e.g., immediately after gateway/node startup).
2. `handler.HandleJSONRPCUserMessage` sees `cachedPublicKey == nil`, creates an active request, and calls `handlePublicKeyGet`, which calls `fanOutToVaultNodes`, forwarding the untouched request (with nil `Params`) to every DON node.
3. Each node's `GatewayHandler.HandleGatewayMessage` routes the request to `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)`; since `req.Params` is nil, this dereference panics with "invalid memory address or nil pointer dereference," disrupting Vault handling on every DON node that received the forwarded message.

Note: I was unable to fully confirm from static analysis whether a `recover()` exists somewhere higher in the goroutine stack (e.g., in the gateway connector's message dispatch loop) that would turn this panic into a caught error rather than a full process crash; this should be verified with a live reproduction/test run to determine whether the blast radius is "goroutine crash" or "full node/gateway process crash."

### Citations

**File:** core/capabilities/vault/gw_handler.go (L207-208)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
```

**File:** core/capabilities/vault/gw_handler.go (L275-279)
```go
func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L338-342)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L364-368)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-416)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
			// Not found in cache. Fetch from nodes.
			ar, err := h.newActiveRequest(req, callback)
			if err != nil {
				h.lggr.Errorw("failed to create new activeRequest", "error", err)
				return err
			}
			return h.handlePublicKeyGet(ctx, ar)
```

**File:** core/services/gateway/handlers/vault/handler.go (L692-708)
```go
func (h *handler) handlePublicKeyGet(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
	if cachedPublicKey != nil {
		l.Debugw("returning cached public key response")
		return h.sendSuccessResponse(ctx, l, ar, &jsonrpc.Response[json.RawMessage]{
			Version: jsonrpc.JsonRpcVersion,
			ID:      ar.req.ID,
			Method:  ar.req.Method,
			Result:  (*json.RawMessage)(&publicKeyResponseBytes),
		})
	}

	l.Debugw("cache stale: forwarding request to nodes", "now", h.clock.Now())
	return h.fanOutToVaultNodes(ctx, l, ar)
}
```

**File:** core/services/gateway/handlers/vault/handler.go (L736-752)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}

	if len(nodeErrors) == len(h.donConfig.Members) && len(nodeErrors) > 0 {
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("failed to forward user request to nodes"), nil))
	}

	l.Debugw("successfully forwarded request to Vault nodes")
	return nil
}
```
