### Title
Nil-Pointer Dereference DoS in Vault Node `MethodPublicKeyGet` Handler via Unrecovered Gateway Read Loop - (File: core/capabilities/vault/gw_handler.go)

### Summary
The `MethodPublicKeyGet` gateway-message handler on the vault node side dereferences `req.Params` without checking for `nil`, unlike every sibling handler in the same file. A crafted JSON-RPC request with `params` omitted reaches this code path through the node's `gatewayConnector.readLoop`, which invokes handlers synchronously with no `recover()`, so the resulting panic crashes the node process — the same bug class as CVE-2021-46049 (unchecked pointer dereference → Denial of Service).

### Finding Description
`GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` straight to `handlePublicKeyGet` with no params-presence check: [1](#0-0) 

`handlePublicKeyGet` unmarshals `*req.Params` immediately: [2](#0-1) 

If `req.Params` is `nil`, `*req.Params` panics with a nil-pointer dereference. Every other method in the same handler (`MethodSecretsCreate`/`Update`/`Delete`/`List`) is routed either through `requestProcessor.ProcessRequest`, which validates request structure, or via handlers that also dereference `*req.Params` without a nil guard (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList` all have the identical unguarded pattern): [3](#0-2) [4](#0-3) [5](#0-4) 

Compare this to the confidential-relay handler in the same codebase, which explicitly guards `req.Params == nil` before use: [6](#0-5) 

Crucially, the message reaches the node handler directly from the network read loop, with no panic recovery: [7](#0-6) 

`readLoop` only decodes the outer JSON-RPC envelope (`req`) and dispatches by `req.Method` to the registered handler — `req.Params` itself is never required to be non-nil at this layer, so a `params`-less `vault.publicKeyGet` request passes straight through to `handlePublicKeyGet`.

### Impact Explanation
Because `readLoop` calls `handler.HandleGatewayMessage` synchronously in the connector's single per-gateway read goroutine with no `recover()`, an unrecovered panic here is fatal to the Go process by default, crashing the entire chainlink node (not just the goroutine). This is a Denial of Service against the node process, reachable via a message that only needs to traverse the untrusted gateway ingress path (the same "internet-facing gateway message envelope/handler" surface called out in scope), analogous to the GPAC `gf_fileio_check` pointer-dereference DoS.

### Likelihood Explanation
Likelihood is high for any actor able to reach the gateway HTTP endpoint and route a `vault.publicKeyGet` JSON-RPC request with `params` omitted (or explicitly `null`) to a subscribed node/DON — this is normally an unprivileged/public-facing request path since `MethodPublicKeyGet` requires no prior authorization step (unlike `SecretsCreate`/`Update` which first require `getMasterPublicKey`/`ProcessRequest`, and unlike `SecretsDelete`/`List` which go through `ProcessRequest`). The `handlePublicKeyGet` case is dispatched with zero validation before crash.

### Recommendation
Add an explicit `req.Params == nil` check in `handlePublicKeyGet` (and the other `handleSecrets*` functions for defense-in-depth) that returns a `UserMessageParseError`/`InvalidParamsError` response instead of dereferencing a nil pointer, mirroring the pattern already used in `core/capabilities/confidentialrelay/handler.go`. Additionally, consider wrapping `readLoop`'s handler dispatch in a `recover()` so a bug in any one handler cannot take down the whole node process.

### Proof of Concept
1. Attacker sends (or a compromised/spoofed client sends through the gateway) a JSON-RPC request to the gateway with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault_publicKeyGet"}
```
(no `params` field, so `req.Params` decodes to `nil`).
2. Gateway forwards this to the subscribed vault node(s) via `SendToGateway`/websocket; node's `readLoop` decodes it into `jsonrpc.Request[json.RawMessage]{Params: nil}` and dispatches to `GatewayHandler.HandleGatewayMessage`.
3. `HandleGatewayMessage` matches `case vaulttypes.MethodPublicKeyGet:` and calls `h.handlePublicKeyGet(ctx, gatewayID, req)` with no nil check.
4. `json.Unmarshal(*req.Params, r)` dereferences the nil `*json.RawMessage` pointer, causing a runtime panic.
5. Because `readLoop` has no `recover()`, the panic propagates up and crashes the node process, producing a Denial of Service.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L207-211)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
	default:
		response = h.errorResponse(ctx, gatewayID, req, api.UnsupportedMethodError, errors.New("unsupported method: "+req.Method))
	}
```

**File:** core/capabilities/vault/gw_handler.go (L275-279)
```go
func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L313-317)
```go
func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L338-342)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
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

**File:** core/capabilities/confidentialrelay/handler.go (L332-335)
```go
func (h *Handler) handleSecretsGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	if req.Params == nil {
		return h.errorResponse(ctx, gatewayID, req, jsonrpc.ErrInvalidParams, errors.New("missing params"))
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
