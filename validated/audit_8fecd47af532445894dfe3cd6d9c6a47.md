## Analog Found

### Title
Unauthenticated NULL/Nil Pointer Dereference in Vault Gateway Handler `handlePublicKeyGet` Crashes Node - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
CVE-2021-3480 describes a NULL pointer dereference during parsing of an unauthenticated Binding DN in slapi-nis that crashes the directory server. The chainlink node-side Vault gateway handler contains an analogous unauthenticated-input NULL pointer dereference: the `vault.publicKey.get` code path skips the params-nil validation performed for every other Vault method, and directly dereferences a possibly-nil pointer while parsing the JSON-RPC request forwarded from an external, unauthenticated client through the internet-facing Gateway.

### Finding Description
On the node side, `GatewayHandler.HandleGatewayMessage` dispatches incoming JSON-RPC requests from the Gateway based on `req.Method`: [1](#0-0) 

For `vaulttypes.MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, and `MethodSecretsList`, the request is first routed through `h.requestProcessor.ProcessRequest`, whose per-method handlers explicitly reject a nil `req.Params`: [2](#0-1) 

However, for `vaulttypes.MethodPublicKeyGet`, the code calls `h.handlePublicKeyGet` **directly**, bypassing `requestProcessor.ProcessRequest` and its nil-params check entirely: [3](#0-2) 

`handlePublicKeyGet` unconditionally dereferences `*req.Params`: [4](#0-3) 

If `req.Params` is `nil` (i.e. the JSON-RPC request omits the `"params"` field, which is legal per JSON-RPC 2.0), `*req.Params` panics with a nil pointer dereference.

On the Gateway side, `handler.HandleJSONRPCUserMessage` treats `vault.publicKey.get` as not requiring authorization and forwards it to nodes with no `params`-presence validation at all — it is the only method exempted from `requestProcessor.ProcessRequest`'s nil-params check: [5](#0-4) 

The Gateway then fans this untouched request out to every node in the DON via `SendToNode`: [6](#0-5) 

On the node, the forwarded request is read and dispatched with no panic recovery: [7](#0-6) 

Because Go panics are fatal to the whole process unless recovered somewhere in the call stack, and no `recover()` exists between `readLoop` and `handlePublicKeyGet`, a crafted `vault.publicKey.get` request with `params` omitted or `null` will crash the node process handling Vault gateway traffic — directly mirroring CVE-2021-3480's "unauthenticated NULL pointer dereference during parsing causing service crash / availability loss."

### Impact Explanation
An unauthenticated, unprivileged external actor can reach every node in a DON that runs the Vault capability's gateway connector simply by sending a JSON-RPC request with method `vault.publicKey.get` and no `params` field through the internet-facing Gateway. This bypasses the one place other Vault methods validate for nil params, and results in an unrecovered panic on the node, crashing node availability (matching the CVSS "C:N/I:N/A:H" profile of the source CVE).

### Likelihood Explanation
High. The attack requires only a single unauthenticated HTTP/WebSocket request to the public Gateway endpoint with a trivially malformed JSON-RPC payload (`{"jsonrpc":"2.0","id":"x","method":"vault.publicKey.get"}` with no `params`), and this method is intentionally exempted from authorization per the code comment "Public key requests don't require authorization." No credentials, allowlist membership, or prior state is needed.

### Recommendation
Add an explicit `req.Params == nil` check in `GatewayHandler.handlePublicKeyGet` (and, defensively, before dispatch in `HandleGatewayMessage` for `MethodPublicKeyGet`), returning a `UserMessageParseError` response instead of dereferencing a nil pointer, consistent with the existing checks in `GatewayVaultRequestProcessor`'s other method handlers. Additionally, wrap `HandleGatewayMessage` invocation in `connector.go`'s `readLoop` with `recover()` to prevent any single malformed/handler-bug message from taking down the whole node process.

### Proof of Concept
1. Stand up a Gateway + Vault-capability node per normal chainlink deployment.
2. As an unauthenticated client, send to the Gateway's public HTTP endpoint:
```json
{"jsonrpc":"2.0","id":"poc-1","method":"vault.publicKey.get"}
```
(note: no `"params"` key, which is valid JSON-RPC 2.0).
3. Gateway's `handler.HandleJSONRPCUserMessage` treats this method as not requiring authorization/params validation and forwards it unchanged to all DON nodes via `SendToNode`.
4. Each node's `GatewayHandler.HandleGatewayMessage` dispatches directly to `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, panicking with a nil pointer dereference and crashing the node process (no `recover()` present in the call chain from `connector.go`'s `readLoop`).

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

**File:** core/services/gateway/handlers/vault/handler.go (L736-751)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}

	if len(nodeErrors) == len(h.donConfig.Members) && len(nodeErrors) > 0 {
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("failed to forward user request to nodes"), nil))
	}

	l.Debugw("successfully forwarded request to Vault nodes")
	return nil
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
