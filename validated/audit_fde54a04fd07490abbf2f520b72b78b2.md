Audit Report

## Title
NULL Pointer Dereference in Vault Gateway `PublicKeyGet` Handler Crashes Node's Gateway Connector - (File: core/capabilities/vault/gw_handler.go)

## Summary
`GatewayHandler.handlePublicKeyGet` dereferences `req.Params` via `*req.Params` without a nil check, unlike every other branch in `HandleGatewayMessage`. The `vault.publicKey.get` method is dispatched to this handler before any authorization/allowlist check runs, so a JSON-RPC message with `params` omitted or `null` reaches the unguarded dereference and panics in the connector's read-loop goroutine, which has no `recover()`.

## Finding Description
`HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` straight to `handlePublicKeyGet`, bypassing `h.requestProcessor.ProcessRequest`/`Authorizer.AuthorizeRequest` entirely, unlike `MethodSecretsCreate/Update/Delete/List`: [1](#0-0) 

`handlePublicKeyGet` then unmarshals directly into `*req.Params`: [2](#0-1) 

Every other handler on this same struct (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) performs the identical `json.Unmarshal(*req.Params, ...)` pattern, but those are only reached after `ProcessRequest`, which explicitly guards `if req.Params == nil` and returns an error instead: [3](#0-2)  `handlePublicKeyGet` has no equivalent guard and is dispatched before any such check, so `req.Params == nil` (as happens when a JSON-RPC message omits `params` or sets it to `null`) causes `*req.Params` to panic.

This message originates from the gateway connector's `readLoop`, which unmarshals the raw JSON-RPC request and invokes `handler.HandleGatewayMessage` synchronously in a per-gateway goroutine, with no `recover()` anywhere in the connector package: [4](#0-3) 

The comparable capability-execute handler in a different package does defend against this exact case (`if req.Params == nil { return errorResponse }`), confirming this is a known, expected precondition that was simply missed for `handlePublicKeyGet`. The panic is unrecovered and, per Go semantics, terminates the goroutine's enclosing program (crashes the node process) rather than merely being caught. Because `MethodPublicKeyGet` is intentionally excluded from `AuthorizeRequest`, no allowlist/JWT authorization is needed to reach the vulnerable code — only the ability to send a message to the gateway targeting the Vault DON with method `vault.publicKey.get` and `params: null`.

## Impact Explanation
An unrecovered panic in the connector's read-loop goroutine crashes the node process, disconnecting it from the gateway entirely — a concrete, in-scope denial-of-service condition triggerable without any privileged credential, matching the "unauthorized denial of service via crash" class of issue. This is a legitimate, low-effort DoS against any Chainlink node running the Vault gateway handler.

## Likelihood Explanation
High. `vault.publicKey.get` is deliberately exempt from authorization (`AuthorizeRequest`/allowlist) because it is meant to be a low-privilege, public operation, meaning any actor capable of reaching the gateway with a message routed to the Vault DON can trigger it. Constructing a request with `params: null` (or omitted) is trivial and requires no special access.

## Recommendation
Add a `req.Params == nil` guard at the start of `handlePublicKeyGet`, returning an `api.InvalidParamsError`/`api.UserMessageParseError` response (mirroring the check in `GatewayVaultRequestProcessor.ProcessRequest`). As defense in depth, add `recover()` around the `handler.HandleGatewayMessage` dispatch in `gatewayConnector.readLoop` so a single malformed/malicious message from any gateway cannot crash the entire node process.

## Proof of Concept
Send via the gateway to the DON the JSON-RPC request:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get","params":null}
```
This decodes into `jsonrpc.Request[json.RawMessage]{Params: nil}`, is routed to `vaulttypes.MethodPublicKeyGet` in `HandleGatewayMessage` (bypassing `ProcessRequest`/authorization), and `json.Unmarshal(*req.Params, r)` in `handlePublicKeyGet` panics on the nil pointer dereference inside `gatewayConnector.readLoop`, crashing the process since there is no `recover()` in the call chain. A Go unit test constructing such a request and calling `GatewayHandler.HandleGatewayMessage` directly would demonstrate the panic.

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L114-117)
```go
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
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
