This is a genuine nil-pointer-dereference DoS analog to CVE-2017-9217 (crash on an unexpected/missing field). The gateway explicitly allows unauthenticated `vault_publicKeyGet` requests with no params validation, and the DON-side handler dereferences the params pointer unconditionally.

### Title
Node crash via nil-params `vault_publicKeyGet` request bypassing params validation - (File: core/capabilities/vault/gw_handler.go)

### Summary
The Vault gateway explicitly treats `MethodPublicKeyGet` as not requiring authorization or params validation, per the comment in `HandleJSONRPCUserMessage`: "Public key requests don't require authorization... Let's process this request right away," which forwards the raw request straight to `fanOutToVaultNodes`/DON nodes without ensuring `Params` is non-nil. [1](#0-0) 

### Finding Description
On the node side, `GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet` without going through `GatewayVaultRequestProcessor.ProcessRequest` (which is the only place that checks `req.Params == nil` for the other vault methods, e.g. `processCreateSecretsRequest`, `processDeleteSecretsRequest`). [2](#0-1) [3](#0-2) 

`handlePublicKeyGet` then unconditionally dereferences `*req.Params`:
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
``` [4](#0-3) 

If `req.Params` is `nil` (a JSON-RPC request with `"params": null` or the field omitted), `*req.Params` is a nil-pointer dereference, which panics. This is reached from `connector.go`'s `readLoop`, which calls `handler.HandleGatewayMessage` directly in the connector's read goroutine with no `recover()` guarding it: [5](#0-4) 

This mirrors the root cause of CVE-2017-9217: a message that omits an expected structural element (there, DNS question section; here, the JSON-RPC `params` field) crashes the daemon because the parser assumes the field is always present.

### Impact Explanation
An unauthenticated crash of this goroutine will propagate as an unrecovered panic, crashing the entire `chainlink` node process (Go panics in a goroutine terminate the whole program unless recovered). Because `vault_publicKeyGet` is explicitly exempted from authorization by design (per the code comment), this is reachable by any client able to reach the gateway HTTP endpoint that a node connects to — no valid workflow owner, JWT, or allowlist entry is required.

### Likelihood Explanation
High. The `HandleJSONRPCUserMessage` code path is specifically designed to fast-path `MethodPublicKeyGet` requests without authorization, and nothing in that path or in `GatewayHandler.HandleGatewayMessage`/`handlePublicKeyGet` on the node validates `Params` before dereferencing it. Existing tests only exercise `Params: nil` through the gateway-side handler (`TestVaultHandler_PublicKeyGet`), not through the node-side `GatewayHandler.HandleGatewayMessage`/`handlePublicKeyGet` path shown above, so this specific gap is not covered by the current test suite. [6](#0-5) 

### Recommendation
Add an explicit `req.Params == nil` (and, if non-nil, valid-JSON) check in `GatewayHandler.handlePublicKeyGet` (and any other handler branch reached from `HandleGatewayMessage` without going through `GatewayVaultRequestProcessor`) before dereferencing/unmarshalling, returning a JSON-RPC error response instead of panicking. Also consider wrapping `handler.HandleGatewayMessage` calls in `connector.go`'s `readLoop` with a `recover()` to prevent any single malformed/malicious message from taking down the whole node process.

### Proof of Concept
1. As an unauthenticated client, send to the gateway's vault HTTP endpoint:
```json
{"jsonrpc":"2.0","id":"poc-1","method":"vault_publicKeyGet","params":null}
```
2. The gateway (`handler.HandleJSONRPCUserMessage`) skips authorization/validation for `MethodPublicKeyGet` and, since no cached public key exists yet (e.g., right after node/gateway startup or cache expiry), forwards the raw request to a DON node via `fanOutToVaultNodes`.
3. On the DON node, `connector.go`'s `readLoop` unmarshals the request (`Params` remains `nil`) and calls `GatewayHandler.HandleGatewayMessage`, which routes to `handlePublicKeyGet`.
4. `json.Unmarshal(*req.Params, r)` dereferences the nil `*json.RawMessage`, causing a panic that is unrecovered in the read loop, crashing the node process.

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L91-107)
```go
func (p *GatewayVaultRequestProcessor) processRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	switch req.Method {
	case vaulttypes.MethodSecretsCreate:
		return p.processCreateSecretsRequest(ctx, req, publicKey)
	case vaulttypes.MethodSecretsUpdate:
		return p.processUpdateSecretsRequest(ctx, req, publicKey)
	case vaulttypes.MethodSecretsDelete:
		return p.processDeleteSecretsRequest(ctx, req)
	case vaulttypes.MethodSecretsList:
		return p.processListSecretIdentifiersRequest(ctx, req)
	default:
		return nil, fmt.Errorf("unsupported gateway vault method: %s", req.Method)
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1289-1297)
```go
	jsonRequest := jsonrpc.Request[json.RawMessage]{
		ID:     "request_id",
		Method: vaulttypes.MethodPublicKeyGet,
		Params: nil,
	}
	ar, err := h.(*handler).newActiveRequest(jsonRequest, callback)
	require.NoError(t, err)
	err = h.(*handler).handlePublicKeyGet(t.Context(), ar)
	require.NoError(t, err)
```
