Audit Report

## Title
Nil-pointer panic in Vault gateway handler's `handlePublicKeyGet` when JSON-RPC request omits `params` - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without passing them through `GatewayVaultRequestProcessor.ProcessRequest`, unlike the create/update/delete/list methods. `handlePublicKeyGet` unconditionally dereferences `*req.Params`, which is an optional `*json.RawMessage` field that can legitimately be `nil`, causing a panic that crashes the connector's `readLoop` goroutine since there is no `recover()` in that loop.

## Finding Description
In `HandleGatewayMessage`, the four secrets methods (`create`, `update`, `delete`, `list`) are first run through `h.requestProcessor.ProcessRequest`, and each of the corresponding processor functions (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) explicitly checks `if req.Params == nil` and returns an `InvalidVaultParamsError` before ever dereferencing `req.Params`: [1](#0-0) 
This nil-check protects `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, and `handleSecretsList`, because the dispatch code in `HandleGatewayMessage` only calls those handlers when `response == nil`, i.e., only after `ProcessRequest` has already succeeded (which requires non-nil `Params`): [2](#0-1) 

However, `vaulttypes.MethodPublicKeyGet` is dispatched directly to `handlePublicKeyGet` with no equivalent validation step: [3](#0-2) 
`handlePublicKeyGet` immediately dereferences `*req.Params` with no nil check: [4](#0-3) 
This is a genuine, reachable bug distinct from the claim's assertion that all five handlers share the flaw — the create/update/delete/list handlers are safe because of the upstream `ProcessRequest` validation, but `handlePublicKeyGet` is not.

On the node side, the connector's `readLoop` invokes `handler.HandleGatewayMessage` synchronously with no `recover()` anywhere in that file, confirmed by a repo-wide search for `recover()` in `core/services/gateway/connector/` returning no matches: [5](#0-4) 
Therefore a panic in `handlePublicKeyGet` propagates uncaught and crashes the `readLoop` goroutine for that gateway connection.

## Impact Explanation
An unprivileged client can send a `vault.getPublicKey` JSON-RPC request with `params` omitted or `null` through the Gateway's public HTTP endpoint. The gateway forwards the request without requiring `Params` presence, reaching the node's `handlePublicKeyGet`, which panics on `json.Unmarshal(*req.Params, r)`. Because `readLoop` has no panic recovery, this crashes the goroutine responsible for processing all further Vault messages from that gateway connection, denying legitimate `vault.getPublicKey`, `createSecrets`, `updateSecrets`, `deleteSecrets`, and `listSecrets` operations routed through that connection — a concrete availability/DoS impact on a security-sensitive capability (Vault secrets management), matching Chainlink's in-scope "node API" denial-of-service impact class.

## Likelihood Explanation
High likelihood for the `handlePublicKeyGet` path specifically: no authentication or special privilege is needed — any client able to reach the gateway's public Vault endpoint can send a `vault.getPublicKey` request without a `params` field. There is no field-presence validation on this specific path before the unguarded dereference. This narrows the original report, which incorrectly claimed the vulnerability also applies to `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, and `handleSecretsList` — those are already protected by explicit nil checks in `gateway_vault_request_processor.go` and are not exploitable this way.

## Recommendation
Add an explicit nil check for `req.Params` in `handlePublicKeyGet` (returning a `UserMessageParseError`/invalid-params response via `h.errorResponse`), consistent with the pattern already used in `gateway_vault_request_processor.go`. As defense-in-depth, wrap the `handler.HandleGatewayMessage` call in `connector.readLoop` (`core/services/gateway/connector/connector.go`) with a `recover()` so a panic in any handler cannot take down the whole read loop for a gateway connection.

## Proof of Concept
1. Send a JSON-RPC request to the Gateway's public HTTP endpoint targeting the Vault service, method `vault.getPublicKey`, with the `params` field omitted or explicitly `null`.
2. The Gateway forwards the request to the Vault DON node via the connector without validating `Params` presence for this method.
3. On the node, `connector.readLoop` calls `GatewayHandler.HandleGatewayMessage`, which routes directly to `handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go:364-368`), executing `json.Unmarshal(*req.Params, r)` — dereferencing a nil pointer panics.
4. The panic propagates up through `readLoop` (no `recover()` present), crashing that goroutine and halting further Vault message processing for the affected gateway connection on the node.

A Go unit test invoking `GatewayHandler.HandleGatewayMessage` with a `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` would reproduce the panic directly.

### Citations

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

**File:** core/capabilities/vault/gw_handler.go (L187-224)
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

	if response == nil {
		switch req.Method {
		case vaulttypes.MethodSecretsCreate:
			response = h.handleSecretsCreate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsUpdate:
			response = h.handleSecretsUpdate(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsDelete:
			response = h.handleSecretsDelete(ctx, gatewayID, req)
		case vaulttypes.MethodSecretsList:
			response = h.handleSecretsList(ctx, gatewayID, req, authResult)
		}
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
