### Title
Unauthenticated NULL Pointer Dereference in Vault `publicKeyGet` Gateway Message Handler - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The node-side Vault `GatewayHandler.HandleGatewayMessage` dereferences `req.Params` without a nil check when handling the `vault.publicKeyGet` method, unlike the other Vault methods (`secretsCreate`, `secretsUpdate`, `secretsDelete`, `secretsList`) which are first routed through `h.requestProcessor.ProcessRequest`, whose downstream validators reject nil params before any unmarshalling occurs.

### Finding Description
In `HandleGatewayMessage`, the method dispatch is: [1](#0-0) 

For `vaulttypes.MethodPublicKeyGet`, the handler calls `h.handlePublicKeyGet(ctx, gatewayID, req)` directly — with no prior validation step (no call to `requestProcessor.ProcessRequest`, no nil-params guard) — whereas every other supported method is only reached after `ProcessRequest` succeeds (which internally validates that request params are non-nil, per the "request params must not be nil" checks exercised in `handler_test.go`).

`handlePublicKeyGet` then does: [2](#0-1) 

`req.Params` is typed as `*json.RawMessage` on `jsonrpc.Request[json.RawMessage]`. In JSON-RPC 2.0, the `params` member is optional; a well-formed request can simply omit it. The request is unmarshalled generically upstream, e.g. in the connector read loop: [3](#0-2) 

`json.Unmarshal` into `jsonrpc.Request[json.RawMessage]` leaves `Params` as its nil zero value when the `params` field is absent, and no code between the connector's `readLoop` and `handlePublicKeyGet` checks for that nil before dereferencing it. `*req.Params` on a nil pointer is an immediate Go runtime panic (`nil pointer dereference`).

This differs structurally from the CVE-2018-1000879 root cause only in language/runtime detail (Go panic vs. C NULL deref), but the bug class is the same: parsing of an attacker-controlled, malformed/incomplete message reaches a pointer dereference without a preceding nil-check, because one code path (`publicKeyGet`) was not routed through the same input-validation pipeline as its siblings.

### Impact Explanation
A crafted JSON-RPC request for `vault.publicKeyGet` without a `params` field, sent by any unprivileged client through the gateway, causes an unrecovered nil-pointer panic in the node's message-handling code path. If this handler executes on a goroutine without a top-level `recover()` (the connector's `readLoop` shown above has no recover wrapper around `handler.HandleGatewayMessage`), the panic can crash the node process, resulting in a Denial of Service against a chainlink node's Vault DON participation — reachable purely from an unauthenticated/unprivileged external request via the Gateway, matching the "Crash/DoS via a specially crafted message" impact class of the CVE.

### Likelihood Explanation
The `publicKeyGet` method requires no authorization (explicitly, by design, since it's a public key fetch — see the gateway-side handler comment "Public key requests don't require authorization"). This means the attack requires no credentials, no allowlist membership, and no valid signature — only the ability to reach the gateway's HTTP endpoint and send a message that gets routed to a node's `GatewayHandler`. This makes the likelihood of triggering the crash high for any external actor capable of sending gateway requests.

### Recommendation
Add an explicit nil-check on `req.Params` in `handlePublicKeyGet` (and audit all other `*req.Params` dereferences in `gw_handler.go`, e.g., `handleSecretsCreate`, `handleSecretsUpdate`) before dereferencing, returning a `UserMessageParseError` response instead of panicking. Additionally, wrap `HandleGatewayMessage` invocation in the connector's `readLoop` with a `recover()` to prevent any single malformed handler call from taking down the node process, consistent with defense-in-depth for CWE-476 style bugs.

### Proof of Concept
1. Attacker sends (via the gateway's public HTTP/websocket entrypoint) a JSON-RPC 2.0 request routed to a Vault-DON node:
```json
{
  "jsonrpc": "2.0",
  "id": "attacker-1",
  "method": "vault.publicKeyGet"
}
```
(no `"params"` field).
2. Gateway forwards this to the node via `gatewayConnector`; the node's `readLoop` unmarshals it into `jsonrpc.Request[json.RawMessage]{Params: nil}` and dispatches to `GatewayHandler.HandleGatewayMessage`.
3. Since method is `MethodPublicKeyGet`, `handlePublicKeyGet` is invoked directly (bypassing `ProcessRequest`'s params validation) and executes `json.Unmarshal(*req.Params, r)`, dereferencing the nil `*json.RawMessage`, causing a runtime panic.

Note: I was not able to fully verify from the indexed code whether there is a `recover()` wrapper somewhere higher in the goroutine stack (e.g., in the underlying `chainlink-common` jsonrpc2/connector library, which is outside this repo's index) that might convert this panic into a caught error instead of a full process crash. This is a limitation of the available index; a Devin session with full repo/dependency access would be needed to confirm whether the panic is recovered or propagates to a crash.

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

**File:** core/capabilities/vault/gw_handler.go (L364-368)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
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
