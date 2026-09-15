Audit Report

## Title
NULL Pointer Dereference via Unchecked `req.Params` in Vault `handlePublicKeyGet` - (File: core/capabilities/vault/gw_handler.go)

## Summary
`HandleGatewayMessage` in `GatewayHandler` dispatches `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without going through the `nil`-checked path used by every other Vault method. [1](#0-0)  `handlePublicKeyGet` unconditionally dereferences `*req.Params` via `json.Unmarshal(*req.Params, r)`, whereas the sibling handlers in `GatewayVaultRequestProcessor` explicitly guard against `req.Params == nil` before unmarshalling. [2](#0-1)  A JSON-RPC request for this method with `params` omitted causes a nil-pointer dereference panic.

## Finding Description
The claim is accurate as to the code path: `MethodSecretsCreate`/`Update`/`Delete`/`List` are routed through `ProcessRequest`, whose per-method handlers check `req.Params == nil` before dereferencing, while `MethodPublicKeyGet` bypasses this and goes straight to `handlePublicKeyGet`, which dereferences `req.Params` with no guard. [3](#0-2) 

Requests are read and dispatched in `gatewayConnector.readLoop`, a single long-lived goroutine per gateway connection that calls `handler.HandleGatewayMessage(ctx, ...)` synchronously with no `recover()` anywhere in the call chain (`connector.go`, `gw_handler.go`). [4](#0-3)  Because there is no panic recovery, an unrecovered panic in a goroutine crashes the entire Go process, not merely the goroutine — this is standard Go runtime behavior. This confirms the panic is not merely local/contained but can bring down the whole node process, matching the reported impact.

Reachability: any actor able to reach the node's gateway connector with a syntactically valid JSON-RPC request lacking `params` and method `public_key.get` triggers this before any authorization/allowlist/JWT check, since `handlePublicKeyGet` performs no such check.

## Impact Explanation
An unhandled panic in the gateway message read loop crashes the node process handling Vault capability messages, constituting a denial-of-service against the node. This is a genuine, reachable, unauthenticated crash bug distinct from a benign error response — it is not "theoretical" or speculative, and the code was directly inspected to confirm the missing check and the absence of panic recovery in the call chain.

## Likelihood Explanation
No credentials, prior session, or privileged access are required — only the ability to send a message through the gateway connector addressed to the Vault handler (a capability explicitly designed to accept inbound requests from the connected Gateway/DON). The request is trivial to construct (a JSON-RPC object omitting the optional `params` field for method `public_key.get`), making this repeatable and low-effort to trigger.

## Recommendation
Add an explicit `if req.Params == nil` check at the top of `handlePublicKeyGet`, mirroring the checks in `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest`, returning `api.UserMessageParseError`/`InvalidVaultParamsError` instead of dereferencing a nil pointer. Additionally, consider adding panic recovery around `handler.HandleGatewayMessage` in `gatewayConnector.readLoop` as defense-in-depth against any future unguarded dereference in gateway message handlers.

## Proof of Concept
1. Start a node with the Vault capability's `GatewayHandler` registered against a gateway connector.
2. From a client connected as the Gateway (or anything able to route a message the node treats as coming from a trusted gateway peer), send:
```json
{"jsonrpc":"2.0","id":"1","method":"public_key.get"}
```
omitting the `params` field.
3. `readLoop` unmarshals the request and calls `HandleGatewayMessage`, which routes to `handlePublicKeyGet`, executing `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, panicking on nil pointer dereference. [2](#0-1) 
4. Since no `recover()` guards this call path, the panic propagates and crashes the node process, verifiable via a Go unit test invoking `GatewayHandler.HandleGatewayMessage` with a `req.Params == nil` request for `vaulttypes.MethodPublicKeyGet` and observing the panic.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-211)
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

**File:** core/services/gateway/connector/connector.go (L268-298)
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
	}
```
