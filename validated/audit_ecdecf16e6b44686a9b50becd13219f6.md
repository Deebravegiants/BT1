Audit Report

## Title
Node crash via nil-params `vault_publicKeyGet` request bypassing params validation - (File: core/capabilities/vault/gw_handler.go)

## Summary
The gateway explicitly fast-paths `vault_publicKeyGet` requests around authorization/params validation, and the DON node's handler for this method dereferences `req.Params` without a nil check, causing a panic in an unrecovered goroutine. This is reachable by any unauthenticated client able to reach the gateway's user-facing HTTP endpoint.

## Finding Description
The gateway's `gateway.ProcessRequest` decodes the raw HTTP body into a `jsonrpc.Request[json.RawMessage]` via `jsonrpc2.DecodeRequest` and passes it directly to `h.HandleJSONRPCUserMessage` with no requirement that `Params` be present. [1](#0-0) [2](#0-1) 

In `HandleJSONRPCUserMessage`, `vaulttypes.MethodPublicKeyGet` is explicitly special-cased to skip authorization entirely ("Public key requests don't require authorization... Let's process this request right away") and, when no cached key exists, forwards the raw request (with whatever `Params` value the client sent, including `nil`) straight to `fanOutToVaultNodes`, which sends it unmodified to DON node members. [3](#0-2) [4](#0-3) 

On the node side, `GatewayHandler.HandleGatewayMessage` routes `MethodPublicKeyGet` directly to `handlePublicKeyGet`, bypassing `GatewayVaultRequestProcessor.ProcessRequest` — the only place that validates `req.Params == nil` for the other vault methods. [5](#0-4) 

`handlePublicKeyGet` then unconditionally dereferences the pointer: `json.Unmarshal(*req.Params, r)`. If `Params` is `nil` (client sends `"params": null` or omits the field), this is a nil-pointer dereference that panics. [6](#0-5) 

This request is received by `gatewayConnector.readLoop`, which unmarshals the incoming message and calls `handler.HandleGatewayMessage` directly in the read goroutine with no `recover()` around the call — confirmed by inspection of `connector.go`, which has no `recover()` calls anywhere in the connector package. [7](#0-6)  A panic in this goroutine is unrecovered and crashes the entire node process.

The existing test `TestVaultHandler_PublicKeyGet` only exercises `Params: nil` through the *gateway-side* handler's `newActiveRequest`/`handlePublicKeyGet` path (`core/services/gateway/handlers/vault/handler.go`), not through the *node-side* `GatewayHandler.HandleGatewayMessage`/`handlePublicKeyGet` path in `core/capabilities/vault/gw_handler.go` shown above, so this gap is not covered by the current test suite.

## Impact Explanation
This is a genuine unauthenticated denial-of-service: crashing the node process via a single malformed JSON-RPC request that requires no valid workflow owner, JWT, or allowlist entry, since `vault_publicKeyGet` is explicitly exempted from authorization by design. This maps to a legitimate in-scope DoS impact class (crash of the node process from unprivileged/unauthenticated input), analogous in root cause to CVE-2017-9217 (missing-field assumption crash).

## Likelihood Explanation
High. The code path is deliberately designed to skip authorization for this method, and no validation of `Params` exists anywhere along the path from HTTP ingress to the vulnerable dereference: not in `gateway.ProcessRequest`, not in `HandleJSONRPCUserMessage`'s public-key-get branch, not in `GatewayHandler.HandleGatewayMessage`'s switch-case for `MethodPublicKeyGet`, and not in `handlePublicKeyGet` itself. The only mitigating factor is the public-key response cache (`getCachedPublicKey`), which is bypassed simply by triggering the request when the cache is empty (e.g., at node/gateway startup, or once the 300-second cache expires) — an attacker can always find or force a window where the cache is stale.

## Recommendation
Add an explicit `req.Params == nil` check in `GatewayHandler.handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go`) before dereferencing/unmarshalling, returning a JSON-RPC error response (e.g., via `h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, ...)`) instead of panicking. Audit all other branches reached from `HandleGatewayMessage` that bypass `GatewayVaultRequestProcessor` for the same issue. Additionally, wrap `handler.HandleGatewayMessage` calls in `connector.go`'s `readLoop` with a `recover()` so that any single malformed or malicious message cannot take down the entire node process — defense in depth against similar bugs in other handlers.

## Proof of Concept
1. As an unauthenticated client, send to the gateway's vault HTTP endpoint (immediately after startup/cache expiry so no cached public key exists):
```json
{"jsonrpc":"2.0","id":"poc-1","method":"vault_publicKeyGet","params":null}
```
2. `gateway.ProcessRequest` decodes this and calls `handler.HandleJSONRPCUserMessage`, which skips authorization for `MethodPublicKeyGet`, finds no cached key, and forwards the request via `fanOutToVaultNodes` to DON node members with `Params` still `nil`.
3. On the DON node, `connector.go`'s `readLoop` unmarshals the request and calls `GatewayHandler.HandleGatewayMessage`, which routes to `handlePublicKeyGet`.
4. `json.Unmarshal(*req.Params, r)` in `core/capabilities/vault/gw_handler.go` line 366 dereferences the nil `*json.RawMessage`, panicking in the connector's read goroutine and crashing the node process.

A Go unit test targeting `GatewayHandler.HandleGatewayMessage` (constructing a `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and calling it directly, or via the connector's message-dispatch path) would deterministically reproduce the panic.

### Citations

**File:** core/services/gateway/gateway.go (L221-230)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
```

**File:** core/services/gateway/gateway.go (L270-276)
```go
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
```

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

**File:** core/services/gateway/connector/connector.go (L268-297)
```go
func (c *gatewayConnector) readLoop(gatewayState *gatewayState) {
	defer c.closeWait.Done()
	ctx, cancel := c.shutdownCh.NewCtx()
	defer cancel()

	for {
		select {
		case <-c.shutdownCh:
			return
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
		}
```
