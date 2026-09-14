The libjpeg CVE describes a NULL pointer dereference from unvalidated/attacker-controlled input causing a crash (DoS). The closest concrete analog in this codebase is in the Vault capability's gateway-facing JSON-RPC handler, which dereferences `req.Params` without a nil check on a method reachable directly from an unprivileged gateway client.

### Title
NULL pointer dereference DoS via missing `params` field on `vault.publicKey.get` gateway request - (File: core/capabilities/vault/gw_handler.go)

### Summary
`GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet` without first validating that `req.Params` is non-nil, unlike the other vault methods which are routed through `requestProcessor.ProcessRequest` (which rejects nil params). `handlePublicKeyGet` immediately dereferences `*req.Params`, causing a nil-pointer panic if an attacker sends a request with a missing/omitted `params` field.

### Finding Description
In the method dispatch switch of `HandleGatewayMessage`: [1](#0-0) 

`vaulttypes.MethodSecretsCreate/Update/Delete/List` all pass through `h.requestProcessor.ProcessRequest(ctx, req, ...)` before any handler touches `req.Params`, and that pipeline explicitly rejects nil params (confirmed by the existing test `TestGatewayVaultRequestProcessor_ProcessRequest_RejectsNilParams`): [2](#0-1) 

However, `vaulttypes.MethodPublicKeyGet` goes straight to `handlePublicKeyGet`, which unconditionally dereferences the pointer: [3](#0-2) 

If `req.Params` is `nil` (e.g., the JSON-RPC request omits the `params` field entirely — `jsonrpc.Request.Params` is `*json.RawMessage`), `*req.Params` panics with a nil-pointer dereference.

This handler is invoked from the gateway connector's read loop with no panic recovery anywhere in the call chain: [4](#0-3) 

A `recover()` was searched for across `core/services/gateway/**` and none exists in the connector or handler dispatch path, so a panic here is unrecovered and crashes the node process (a websocket message read loop running the handler synchronously).

### Impact Explanation
An unprivileged, unauthenticated (pre-authorization) actor able to send `vault.publicKey.get` gateway JSON-RPC messages (this method is intentionally unauthenticated, since it runs before the `getMasterPublicKey`/auth pipeline) can crash the node's process handling that gateway connection by omitting `params`, causing a denial of service that matches the CVE-2021-39517 bug class (NULL pointer dereference from external input → crash).

### Likelihood Explanation
High likelihood: `MethodPublicKeyGet` requires no prior authorization/allowlist check (it bypasses `requestProcessor.ProcessRequest`), and the trigger is a single malformed/minimal JSON-RPC request with method `vault.publicKey.get` and no `params` field — trivially reachable by any actor capable of sending gateway messages.

### Recommendation
Add a nil/empty check on `req.Params` in `handlePublicKeyGet` (and audit all other handler methods reachable pre-authorization for the same pattern), returning a `UserMessageParseError` response instead of dereferencing the raw pointer, mirroring the validation already done by `requestProcessor.ProcessRequest`/`GatewayVaultRequestProcessor`. Additionally, consider adding panic recovery around `handler.HandleGatewayMessage` invocation in the connector `readLoop` as defense-in-depth.

### Proof of Concept
Send a gateway JSON-RPC message with the vault handler's method set but no `params` key:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
This decodes to a `jsonrpc.Request[json.RawMessage]` with `Params == nil`. Dispatch reaches `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` — dereferencing the nil `*json.RawMessage` pointer and panicking in the connector's `readLoop` goroutine, with no recovery in the call path.

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

**File:** core/capabilities/vault/validate_user_request_test.go (L21-37)
```go
func TestGatewayVaultRequestProcessor_ProcessRequest_RejectsNilParams(t *testing.T) {
	t.Parallel()

	validator, err := vault.NewRequestValidatorFromLimitsFactory(limits.Factory{Settings: cresettings.DefaultGetter})
	require.NoError(t, err)

	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-1",
		Method: vaulttypes.MethodSecretsCreate,
	}

	authorizer := vaultcapmocks.NewAuthorizer(t)
	processor := mustNewGatewayVaultRequestProcessor(t, validator, authorizer, false)
	err = processRequestErr(processor, t, &req)
	require.Error(t, err)
	require.True(t, vault.IsInvalidVaultParamsError(err))
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
