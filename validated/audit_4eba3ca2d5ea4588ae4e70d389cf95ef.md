Audit Report

## Title
Nil-pointer panic on unprivileged vault `publicKey.get` gateway request - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet`, bypassing `GatewayVaultRequestProcessor`, which is the only place that performs a `req.Params == nil` check before unmarshalling. `handlePublicKeyGet` unconditionally dereferences `*req.Params` in `json.Unmarshal(*req.Params, r)`, causing a nil-pointer panic if `Params` is nil.

## Finding Description
`HandleGatewayMessage`'s switch statement sends `MethodSecretsCreate/Update/Delete/List` through `h.requestProcessor.ProcessRequest`, whose per-method handlers (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) all begin with an explicit `if req.Params == nil { return ... }` guard [1](#0-0) [2](#0-1) [3](#0-2) . `MethodPublicKeyGet` skips this processor entirely: `case vaulttypes.MethodPublicKeyGet: response = h.handlePublicKeyGet(ctx, gatewayID, req)` [4](#0-3) , and `handlePublicKeyGet` dereferences `req.Params` with no nil check: `if err := json.Unmarshal(*req.Params, r); err != nil` [5](#0-4) .

Tracing the path from the gateway side confirms this is externally reachable with an unauthenticated/unprivileged request. In `handler.HandleJSONRPCUserMessage`, `MethodPublicKeyGet` is explicitly carved out as needing **no authorization**: "Public key requests don't require authorization... Let's process this request right away" [6](#0-5) . On a cache miss, the gateway calls `handlePublicKeyGet` → `fanOutToVaultNodes`, which forwards `ar.req` (the exact incoming request, including whatever `Params` value the client sent) to every DON node unmodified [7](#0-6) [8](#0-7) . Nowhere in this gateway-side path is `req.Params` checked for nil before or during forwarding — the gateway simply relays the client-supplied envelope to the node, so a client-omitted `params` field survives all the way to the node's `handlePublicKeyGet`.

On the node side, `connector.readLoop` unmarshals the incoming bytes into `jsonrpc.Request[json.RawMessage]` and dispatches directly to `handler.HandleGatewayMessage(ctx, gatewayState.config.ID, &req)` with no `recover()` around the call [9](#0-8) ; a targeted search for `recover()` in `core/services/gateway/**` found no matches, confirming there is no panic-recovery wrapper protecting this call path.

## Impact Explanation
This is a genuine, unauthenticated denial-of-service vector against the DON node's Vault `GatewayConnectorHandler`. An unprivileged external client can send a `vault.publicKey.get` JSON-RPC request with no `params` field (valid per JSON-RPC 2.0, and explicitly exempted from the gateway's authorization step) through the Gateway to the node, triggering `json.Unmarshal(*req.Params, r)` on a nil `*json.RawMessage`, which panics. Since the node's `connector.readLoop` calls `handler.HandleGatewayMessage` synchronously with no `recover()`, this panic will propagate up that goroutine's stack; whether it crashes only that goroutine or, absent any top-level recover elsewhere in the process's goroutine tree, brings down the entire node process, could not be fully confirmed within the indexed codebase, but at minimum this breaks the gateway connector's read loop for that connection — a concrete availability impact against a component that is otherwise supposed to be robust against unauthenticated input. This maps to an in-scope "gateway request" denial-of-service / node availability impact category.

## Likelihood Explanation
High. `vault.publicKey.get` is specifically designed to require no authorization (explicit comment and code path in `handler.go`), so any client capable of reaching the gateway's HTTP JSON-RPC endpoint can send a request with an omitted `params` field — this requires no credentials, no signature, and no special setup, and is fully JSON-RPC 2.0 compliant.

## Recommendation
Add an explicit `if req.Params == nil` check at the top of `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`, mirroring the checks already present in `processCreateSecretsRequest`/`processDeleteSecretsRequest`/etc. in `gateway_vault_request_processor.go`, returning an `api.UserMessageParseError`/`InvalidParamsError` response instead of dereferencing a nil pointer. More broadly, add a `recover()` around handler invocation in `connector.readLoop` (or within `HandleGatewayMessage`) as defense-in-depth against any other unchecked-input panic in gateway-routed handlers.

## Proof of Concept
1. Send a JSON-RPC 2.0 request to the Gateway's vault endpoint with `method: "vault.publicKey.get"` and the `params` field omitted entirely (or `"params": null`).
2. Because `MethodPublicKeyGet` requires no authorization, `handler.HandleJSONRPCUserMessage` in `core/services/gateway/handlers/vault/handler.go` forwards the request unmodified to `fanOutToVaultNodes`, which sends it to every DON node member.
3. On each node, `connector.readLoop` unmarshals the bytes into `jsonrpc.Request[json.RawMessage]` (with `Params == nil`) and calls `GatewayHandler.HandleGatewayMessage`, which matches `case vaulttypes.MethodPublicKeyGet` and calls `handlePublicKeyGet`.
4. `json.Unmarshal(*req.Params, r)` in `handlePublicKeyGet` panics with a nil-pointer dereference, since `req.Params` is `nil`.
5. A Go unit test constructing `&jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and calling `GatewayHandler.HandleGatewayMessage` directly reproduces the panic deterministically without any network/auth setup.

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L115-117)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L198-200)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L230-232)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gw_handler.go (L207-208)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
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

**File:** core/services/gateway/handlers/vault/handler.go (L736-744)
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
```

**File:** core/services/gateway/connector/connector.go (L277-296)
```go
		case item := <-gatewayState.conn.ReadChannel():
			var req jsonrpc.Request[json.RawMessage]
			err := json.Unmarshal(item.Data, &req)
			if err != nil {
				c.lggr.Errorw("parse error when reading from Gateway", "id", gatewayState.config.ID, "err", err)
				break
			}
			c.handlersMu.RLock()
			handler, exists := c.handlers[req.Method]
			c.handlersMu.RUnlock()
			if !exists {
				c.lggr.Errorw("no handler for method", "id", gatewayState.config.ID, "method", req.Method)
				break
			}
			// do not break on error. HandleGatewayMessage handles errors
			// by sending a response back to the Gateway.
			err = handler.HandleGatewayMessage(ctx, gatewayState.config.ID, &req)
			if err != nil {
				c.lggr.Warnw("failed to handle message from Gateway", "id", gatewayState.config.ID, "method", req.Method, "err", err)
			}
```
