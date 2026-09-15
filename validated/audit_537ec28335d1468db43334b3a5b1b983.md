Confirmed: at the internet-facing gateway handler (`core/services/gateway/handlers/vault/handler.go`, `HandleJSONRPCUserMessage`), `MethodPublicKeyGet` requests are routed to `handlePublicKeyGet`/`fanOutToVaultNodes` with **no check that `req.Params` is non-nil** before the request is forwarded verbatim to the node-side handler via `h.don.SendToNode(ctx, node.Address, &ar.req)`. This means the claim's premise is accurate: no envelope-level validation of `Params` occurs anywhere on the `MethodPublicKeyGet` path (gateway-side or node-side) the way it does for `MethodSecretsCreate/Update/Delete/List`, which go through `GatewayVaultRequestProcessor.ProcessRequest` (both at the gateway and at the node) and explicitly reject nil `Params`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

On the node side, `GatewayHandler.HandleGatewayMessage` dispatches `MethodPublicKeyGet` directly to `handlePublicKeyGet` without any params-nil check, unlike the secrets methods which go through `requestProcessor.ProcessRequest`, and `handlePublicKeyGet` unconditionally dereferences `*req.Params`. [5](#0-4) [6](#0-5) 

The `jsonrpc2.Request[json.RawMessage]` type does not enforce `Params` to be non-nil at decode time in this code path — the connector's `readLoop` uses plain `json.Unmarshal(item.Data, &req)`, so a `params`-omitted JSON-RPC message decodes to `Params == nil` without error, and is forwarded straight through the switch statement in `HandleGatewayMessage` to `handlePublicKeyGet`, causing a nil-pointer dereference panic when `*req.Params` is evaluated. [7](#0-6) 

Route reachability is real (no auth/authz gate exists for `MethodPublicKeyGet` on either the gateway or node side — see the explicit comment "Public key requests don't require authorization" in the gateway handler), and the exploit requires no credentials. [8](#0-7) 

This matches a genuine, unguarded nil-pointer-dereference bug reachable by an unauthenticated Gateway client, causing a panic in the node process that handles the message — an availability/DoS impact on the Vault-capable DON node(s). I could not verify from the indexed code whether a top-level `recover()` wraps the connector's read loop or `HandleGatewayMessage` goroutine (the report itself flags this uncertainty), so whether the blast radius is "single dropped goroutine" vs "full process crash" remains unconfirmed, but a panic during synchronous request handling is nonetheless a concrete, valid DoS-class bug regardless of that detail.

Audit Report

## Title
Nil pointer dereference (node crash / DoS) on `MethodPublicKeyGet` gateway messages missing `params` - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without checking `req.Params != nil`, unlike every other vault method which is routed through `GatewayVaultRequestProcessor.ProcessRequest` (which explicitly rejects nil `Params`). `handlePublicKeyGet` unconditionally dereferences `*req.Params`, and the same absence of validation exists at the internet-facing gateway handler (`core/services/gateway/handlers/vault/handler.go`), so a request with `method: "vault.publicKeyGet"` and no `params` field is forwarded end-to-end and triggers a nil-pointer panic on the DON node.

## Finding Description
`HandleGatewayMessage` routes `MethodSecretsCreate/Update/Delete/List` through `h.requestProcessor.ProcessRequest`, whose method-specific handlers (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) all check `if req.Params == nil` and return `InvalidVaultParamsError` before unmarshalling. `MethodPublicKeyGet` instead calls `h.handlePublicKeyGet(ctx, gatewayID, req)` directly, and that function immediately does `json.Unmarshal(*req.Params, r)` with no nil guard. Upstream, the internet-facing `handler.HandleJSONRPCUserMessage` in `core/services/gateway/handlers/vault/handler.go` also special-cases `MethodPublicKeyGet` (explicitly noting "Public key requests don't require authorization") and forwards the raw request to nodes via `fanOutToVaultNodes`/`don.SendToNode` without any `Params` nil check — the only validation path (`requestProcessor.ProcessRequest`) is bypassed entirely for this method on both the gateway and node side. The connector's `readLoop` decodes incoming gateway messages via plain `json.Unmarshal`, so a JSON-RPC message with `method` set but `params` omitted decodes with `Params == nil` and is dispatched without error.

## Impact Explanation
This causes a real, uncaught nil-pointer dereference panic on the vault DON node processing the message, matching an availability/DoS impact against the Vault capability. Because the gateway's own handler also skips validation before fanning out to all DON members, a single malformed message can potentially be forwarded to and crash/disrupt every member node of the DON simultaneously.

## Likelihood Explanation
Likelihood is high: constructing a JSON-RPC request with method `vault.publicKeyGet` and omitting `params` is trivial, requires no valid credentials, JWT, or allowlist membership, since `MethodPublicKeyGet` is explicitly exempted from authorization checks on both the gateway and node code paths.

## Recommendation
Add an explicit `if req.Params == nil { ... }` guard in `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go` before dereferencing `*req.Params`, mirroring the pattern used in `processCreateSecretsRequest`/`processDeleteSecretsRequest`/`processListSecretIdentifiersRequest`. Apply the same fix to the gateway-side `handlePublicKeyGet`/`HandleJSONRPCUserMessage` in `core/services/gateway/handlers/vault/handler.go`, or better, route `MethodPublicKeyGet` requests through a shared params-validation step before any handler dereferences `Params`.

## Proof of Concept
1. Send a JSON-RPC 2.0 request to the Gateway: `{"jsonrpc":"2.0","id":"1","method":"vault.publicKeyGet"}` (no `params` field).
2. The gateway-side `handler.HandleJSONRPCUserMessage` matches `req.Method == vaulttypes.MethodPublicKeyGet`, skips authorization, and (on cache miss) calls `handlePublicKeyGet` → `fanOutToVaultNodes`, forwarding the request with `Params == nil` to every DON member via `don.SendToNode`.
3. Each node's `connector` readLoop unmarshals the message (`Params` stays nil) and calls `GatewayHandler.HandleGatewayMessage`, which matches `case vaulttypes.MethodPublicKeyGet` and calls `handlePublicKeyGet(ctx, gatewayID, req)` directly.
4. `json.Unmarshal(*req.Params, r)` dereferences the nil `*json.RawMessage`, panicking on every receiving node.
   A minimal Go unit test invoking `GatewayHandler.HandleGatewayMessage` (or the gateway-side `handler.HandleJSONRPCUserMessage`) with a `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` reproduces the panic.

### Citations

**File:** core/services/gateway/handlers/vault/handler.go (L404-420)
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
		}
		h.lggr.Debugw("returning cached public key response")
		return h.handlePublicKeyGetSynchronously(ctx, req, publicKeyResponseBytes, callback)
	}
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

**File:** core/capabilities/vault/gw_handler.go (L207-211)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-200)
```go
func (p *GatewayVaultRequestProcessor) processDeleteSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/services/gateway/connector/connector.go (L277-293)
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
```
