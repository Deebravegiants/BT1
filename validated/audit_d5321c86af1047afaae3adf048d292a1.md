### Title
NULL pointer dereference in Vault node-side `PublicKeyGet` handler due to missing params nil-check - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault node-side gateway handler dereferences `*req.Params` in `handlePublicKeyGet` without first checking whether `Params` is `nil`, unlike every other Vault JSON-RPC method (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`), which are routed through `GatewayVaultRequestProcessor` and explicitly guarded with `if req.Params == nil { ... }` checks. A crafted `vault_publicKeyGet` request with an omitted/null `params` field causes a Go nil-pointer-dereference panic in the node process — the same bug class as CVE-2021-32283 (NULL pointer dereference from malformed input causing denial of service), just in Go rather than C.

### Finding Description
`GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` directly to `h.handlePublicKeyGet(ctx, gatewayID, req)` [1](#0-0) , bypassing `h.requestProcessor.ProcessRequest`, which is the component that performs the `req.Params == nil` validation used for the other four Vault methods [2](#0-1) .

`handlePublicKeyGet` then unmarshals directly from the pointer without a nil guard: [3](#0-2) 

Contrast this with `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest`, all of which check for nil params before dereferencing: [4](#0-3) 

`GatewayVaultRequestProcessor.processRequest`'s method switch does not even have a case for `MethodPublicKeyGet` — it falls into the `default` branch returning "unsupported gateway vault method", confirming that `PublicKeyGet` was never intended to flow through the processor's nil-check gate [5](#0-4) .

`*json.RawMessage` is a pointer type; when `req.Params` is `nil` (e.g., the JSON-RPC request omits the `"params"` key, or explicitly sets `"params": null`), `json.Unmarshal(*req.Params, r)` dereferences a nil pointer and panics.

### Impact Explanation
`HandleGatewayMessage` is the `GatewayConnectorHandler` entry point that a node's gateway connector invokes for every message it reads from the Gateway (`readLoop` in `core/services/gateway/connector/connector.go` unmarshals the wire JSON-RPC request and calls the registered handler directly, with no pre-validation of `Params`) [6](#0-5) . A panic here crashes/derails the goroutine handling gateway traffic for that node (denial of service against the Vault capability handling on that node), matching the CVE's "NULL pointer dereference ... Denial of Service" impact.

### Likelihood Explanation
Likelihood is high for reaching the vulnerable code path: any JSON-RPC message with `method` set to `vaulttypes.MethodPublicKeyGet` and no (or null) `params` field satisfies the trigger. Whether this is reachable from a fully *unauthenticated external client* end-to-end depends on the Gateway's public-facing Vault handler (`core/services/gateway/handlers/vault/handler.go`) forwarding the request unmodified to nodes before params validation — this forwarding path (`HandleJSONRPCUserMessage` → `don.SendToNode`) was not fully verified line-by-line for a nil-params guard in this pass, so it is possible (but unconfirmed) that the gateway's own JSON-RPC decoding stage rejects a request with entirely missing params before forwarding. Regardless, this is the strongest concrete asymmetry found in the codebase: every sibling Vault method is nil-guarded and `PublicKeyGet` is not.

### Recommendation
Add an explicit nil-check for `req.Params` in `handlePublicKeyGet` (and audit any other handler entry points that dereference `*req.Params` directly, e.g., `handleSecretsCreate`/`Update`/`Delete`/`List` in `gw_handler.go`, which are also unguarded at that layer and only safe today because the processor gates them first — any future refactor removing that ordering would reintroduce the same bug):

```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	if req.Params == nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))
	}
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
	...
```

### Proof of Concept
Send (or have the Gateway forward) a JSON-RPC 2.0 request to a node's Vault gateway connector handler with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault_publicKeyGet"}
```
(no `params` field, or `"params": null`). `req.Params` is `nil`; `HandleGatewayMessage` routes to `handlePublicKeyGet` without going through `GatewayVaultRequestProcessor`; `json.Unmarshal(*req.Params, r)` dereferences the nil pointer and panics.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L207-211)
```go
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L91-108)
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

**File:** core/services/gateway/connector/connector.go (L273-296)
```go
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
```
