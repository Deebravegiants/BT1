Audit Report

## Title
Unprivileged crash of node's Vault gateway handler via nil `Params` on `vault.publicKey.get` - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet` without first passing through `requestProcessor.ProcessRequest`, which is the only code path validating `req.Params != nil` for the other vault methods. `handlePublicKeyGet` unconditionally dereferences `*req.Params`, so a JSON-RPC request for this method that omits `params` causes a nil-pointer dereference panic.

## Finding Description
In `HandleGatewayMessage`, the switch statement sends `MethodSecretsCreate`/`Update`/`Delete`/`List` through `h.requestProcessor.ProcessRequest`, whose per-method handlers (`processCreateSecretsRequest`, `processDeleteSecretsRequest`, etc.) explicitly check `if req.Params == nil { return ... }` before ever unmarshalling. [1](#0-0) [2](#0-1) [3](#0-2) 

`MethodPublicKeyGet`, however, is dispatched straight to `handlePublicKeyGet` with no such guard: [4](#0-3) 

`handlePublicKeyGet` immediately dereferences `*req.Params`: [5](#0-4) 

If `req.Params` is `nil` (a JSON-RPC request that omits the `params` field, valid per the JSON-RPC 2.0 spec for parameterless calls), this dereference panics rather than returning the intended `UserMessageParseError`. The other four handlers (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) have the identical unguarded `*req.Params` pattern, but they are protected because `ProcessRequest`'s nil check runs and short-circuits before those functions are reached — `handlePublicKeyGet` is the only one lacking this upstream guard.

Reachability of this path is confirmed at the transport layer: the connector's `readLoop` reads a raw JSON-RPC message from the gateway websocket, unmarshals it into `jsonrpc.Request[json.RawMessage]` (leaving `Params` as its natural nil value if absent from the wire message), looks up the handler by method name, and calls `handler.HandleGatewayMessage` synchronously, in the same goroutine, with no panic-recovery wrapper visible in that loop: [6](#0-5) 

I was unable to find any `recover()` call wrapping this dispatch path within `core/services/gateway/connector/connector.go`, and I could not fully verify with the tools available whether some outer layer (e.g. a top-level goroutine wrapper elsewhere in the connector's `Start`/run loop) provides panic recovery for `readLoop`. This is a limitation of my verification — I could not conclusively rule out a higher-level recover wrapper, but no such wrapper is visible in the code path examined.

## Impact Explanation
This maps to an availability/DoS impact: a single crafted `vault.publicKey.get` message with no `params` field reaches `handlePublicKeyGet` and panics on `*req.Params` dereference. If `readLoop` is not itself protected by an outer recover, this crashes the goroutine handling all further gateway messages for that connection (and potentially the process, depending on Go runtime panic propagation across goroutines, which by default crashes the whole process unless recovered). This is a legitimate in-scope availability impact analogous to a crash triggered by an unchecked code path on a crafted request — the same class as the referenced ATS ACL segfault. It does not by itself allow secret exfiltration, auth bypass, or fund movement, but node/service disruption from a single unprivileged request is a valid impact class.

## Likelihood Explanation
High. The trigger requires only sending a JSON-RPC request with method `vault.publicKey.get` and no `params` field (or `params: null`) to a reachable gateway-facing endpoint that gets forwarded to node `GatewayHandler.HandleGatewayMessage`. This method is not run through `requestProcessor.ProcessRequest`'s nil-params validation, and the switch statement shows no authorization gate for `MethodPublicKeyGet` either — it is dispatched unconditionally. No credentials, prior state, or special permissions are needed beyond being able to reach the gateway relay for this method.

## Recommendation
Add an explicit nil-params check before calling `handlePublicKeyGet`, mirroring the pattern used in `GatewayVaultRequestProcessor`:
```go
case vaulttypes.MethodPublicKeyGet:
    if req.Params == nil {
        response = h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))
        break
    }
    response = h.handlePublicKeyGet(ctx, gatewayID, req)
```
More robustly, factor a shared nil-check helper used by every method handler (including `handleSecretsCreate/Update/Delete/List` and `handlePublicKeyGet`) so future methods added to the switch cannot bypass validation. Additionally, verify/add panic recovery around `readLoop`'s per-message dispatch in `core/services/gateway/connector/connector.go` as defense-in-depth against any handler panicking.

## Proof of Concept
1. Start a node with the Vault `GatewayHandler` registered against a gateway connector.
2. Send (or emulate the gateway forwarding) a JSON-RPC message over the connector's websocket read channel with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
i.e., omitting `params`.
3. `readLoop` unmarshals this into `jsonrpc.Request[json.RawMessage]{Params: nil}` and calls `handler.HandleGatewayMessage`.
4. `HandleGatewayMessage`'s switch matches `vaulttypes.MethodPublicKeyGet` and calls `handlePublicKeyGet(ctx, gatewayID, req)` directly.
5. `handlePublicKeyGet` executes `json.Unmarshal(*req.Params, r)`, dereferencing the nil `*json.RawMessage` pointer, causing a panic.
A Go unit test constructing `&jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and calling `GatewayHandler.HandleGatewayMessage` directly (as done in `core/capabilities/vault/gw_handler_test.go` for other methods) would reproduce the panic deterministically.

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

**File:** core/capabilities/vault/gw_handler.go (L364-369)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-117)
```go
func (p *GatewayVaultRequestProcessor) processCreateSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-201)
```go
func (p *GatewayVaultRequestProcessor) processDeleteSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
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
