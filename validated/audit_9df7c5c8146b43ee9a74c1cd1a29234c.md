### Title
Nil pointer dereference (node crash / DoS) on `MethodPublicKeyGet` gateway messages missing `params` - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The node-side Vault `GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without validating that `req.Params` is non-nil, unlike every other method on the same dispatch path (`MethodSecretsCreate/Update/Delete/List`), which are routed through `GatewayVaultRequestProcessor.ProcessRequest`, whose per-method handlers (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) all explicitly check `if req.Params == nil` before unmarshalling. `handlePublicKeyGet` skips this check and directly dereferences `*req.Params`.

### Finding Description
`GatewayHandler.HandleGatewayMessage` [1](#0-0)  switches on `req.Method`. For `MethodSecretsCreate`/`MethodSecretsUpdate`/`MethodSecretsDelete`/`MethodSecretsList`, the request is first passed to `h.requestProcessor.ProcessRequest(...)`, which internally calls per-method validators that reject nil `Params` with `InvalidVaultParamsError` before any `json.Unmarshal(*req.Params, ...)` occurs [2](#0-1) [3](#0-2) [4](#0-3) .

For `MethodPublicKeyGet`, however, the handler calls `h.handlePublicKeyGet(ctx, gatewayID, req)` directly with no prior params validation [5](#0-4) . Inside `handlePublicKeyGet`, the code unconditionally dereferences the pointer:

```go
r := &vaultcommon.GetPublicKeyRequest{}
if err := json.Unmarshal(*req.Params, r); err != nil {
``` [6](#0-5) 

If `req.Params` is `nil` (a JSON-RPC request for method `vault.publicKeyGet` with no `params` field), the `*req.Params` dereference panics with a nil pointer dereference, matching the structural bug class in CVE-2017-9468 — a message missing an expected field triggers deref of a nil pointer before any validation occurs.

This request is reachable from an unprivileged client: the request originates at the internet-facing Gateway's `ProcessRequest`, is decoded/validated only at the JSON-RPC envelope level, not the vault-specific params, and is dispatched to node handlers via the connector's `readLoop`, which calls `handler.HandleGatewayMessage` for whatever method name is present [7](#0-6) . `MethodPublicKeyGet` requires no request-level authentication/authorization pre-check (the switch statement in `HandleGatewayMessage` handles it in a separate branch from the auth-checked secrets operations), so any external caller able to route a request to the vault DON with this method name and an omitted `params` field can trigger the panic on every DON node that processes the message.

### Impact Explanation
A panic in the goroutine handling a Gateway message will crash the node process (or at minimum the service, depending on goroutine/recover wiring), producing an availability/DoS impact on the vault-capable node(s) that receive the malformed message. Since these are DON member nodes serving the Vault capability, an attacker could potentially disrupt public-key retrieval and/or crash multiple DON nodes by broadcasting the malformed method to all of them via the Gateway, degrading or halting the secrets/vault capability's availability.

### Likelihood Explanation
Likelihood is high for a caller capable of interacting with the Gateway/JSON-RPC method dispatch: constructing a JSON-RPC request with `method: "vault.publicKeyGet"` (or equivalent constant value of `vaulttypes.MethodPublicKeyGet`) and simply omitting the `params` object is trivial and requires no cryptographic material, valid vault owner, or JWT — the code path that would perform validation/authorization (`requestProcessor.ProcessRequest`) is never invoked for this method.

### Recommendation
Add a nil check for `req.Params` in `handlePublicKeyGet` (and any other gw_handler.go`handle*` helper that dereferences `*req.Params` directly), mirroring the guard already present in `processCreateSecretsRequest`/`processDeleteSecretsRequest`/`processListSecretIdentifiersRequest`, e.g.:
```go
if req.Params == nil {
    return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))
}
```
before the `json.Unmarshal(*req.Params, r)` call at [6](#0-5) . More generally, route `MethodPublicKeyGet` through the same envelope-validation step used for the other vault methods so a single validated code path guarantees non-nil `Params` before any handler dereferences it.

### Proof of Concept
1. Craft a JSON-RPC 2.0 request targeted at a Vault-enabled DON via the Gateway with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKeyGet"}
```
(i.e., method set to the value of `vaulttypes.MethodPublicKeyGet`, with the `params` field entirely omitted).
2. Submit it so it reaches the Gateway's `ProcessRequest` and is routed to the DON's node-side `GatewayConnector`, which forwards it to `GatewayHandler.HandleGatewayMessage`.
3. `HandleGatewayMessage` matches `case vaulttypes.MethodPublicKeyGet:` and calls `handlePublicKeyGet(ctx, gatewayID, req)` directly (no params check).
4. Inside `handlePublicKeyGet`, `json.Unmarshal(*req.Params, r)` dereferences a nil `*json.RawMessage` pointer, causing a runtime panic on the receiving node.

Note: I was unable to directly execute or trace runtime panic-recovery wrapping around `HandleGatewayMessage`/the connector's `readLoop` goroutine within the indexed code, so whether this panic is caught by a top-level `recover()` (limiting impact to a dropped goroutine rather than full node crash) could not be fully confirmed from the available context; a Devin session with full repository/runtime access would be needed to verify the exact blast radius (single goroutine vs. process crash).

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-122)
```go
func (p *GatewayVaultRequestProcessor) processCreateSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var createReq vaultcommon.CreateSecretsRequest
	if err := json.Unmarshal(*req.Params, &createReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-204)
```go
func (p *GatewayVaultRequestProcessor) processDeleteSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var deleteReq vaultcommon.DeleteSecretsRequest
	if err := json.Unmarshal(*req.Params, &deleteReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L226-237)
```go
func (p *GatewayVaultRequestProcessor) processListSecretIdentifiersRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}

	var listReq vaultcommon.ListSecretIdentifiersRequest
	if err := json.Unmarshal(*req.Params, &listReq); err != nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
	}
```

**File:** core/services/gateway/connector/connector.go (L277-296)
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
			if err != nil {
				c.lggr.Warnw("failed to handle message from Gateway", "id", gatewayState.config.ID, "method", req.Method, "err", err)
			}
```
