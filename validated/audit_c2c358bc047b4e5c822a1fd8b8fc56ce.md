## Finding

### Title
Nil pointer dereference on missing `params` in vault public-key-get gateway message handler - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`vaulttypes.MethodPublicKeyGet` is the one vault JSON-RPC method that is deliberately routed around the shared request-validation pipeline (`GatewayVaultRequestProcessor.ProcessRequest`), which is where every other vault method (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`) checks `req.Params == nil` before touching the payload. `handlePublicKeyGet` unconditionally dereferences `*req.Params`, so a request that omits (or nulls) the `params` field panics with a nil pointer dereference, exactly analogous to CVE-2017-12153's missing-attribute-check NULL dereference in `nl80211_set_rekey_data()`.

### Finding Description
`GatewayHandler.HandleGatewayMessage` dispatches by method: [1](#0-0) 

For `MethodSecretsCreate/Update/Delete/List` it always goes through `h.requestProcessor.ProcessRequest(...)` first, and every one of those processing functions guards with `if req.Params == nil { return ... }` before unmarshalling: [2](#0-1) [3](#0-2) 

But `MethodPublicKeyGet` is dispatched directly to `handlePublicKeyGet` with no such guard: [4](#0-3) [5](#0-4) 

`json.Unmarshal(*req.Params, r)` dereferences `req.Params` (a `*json.RawMessage`) directly; if `req.Params` is `nil` this is a nil pointer dereference panic.

The path from an unprivileged client is real: on the gateway side, `handler.HandleJSONRPCUserMessage` treats `MethodPublicKeyGet` as not requiring authorization at all ("Public key requests don't require authorization") and forwards the request (including a possibly-nil `Params`) straight to the DON nodes without validating `req.Params`: [6](#0-5) [7](#0-6) 

The node then receives this via the connector and invokes `GatewayHandler.HandleGatewayMessage`, hitting the unguarded `handlePublicKeyGet`.

I was not able to find (within the indexed content) an explicit `recover()` wrapping the connector's dispatch to `HandleGatewayMessage`, so I cannot fully confirm whether a panic here is caught at a higher level (e.g. an HTTP server middleware) or crashes the node's connector goroutine outright; this is uncertain due to index/tool limits and would need to be confirmed by inspecting `core/services/gateway/connector/connector.go` and the node-side gateway connector wiring in a full checkout.

### Impact Explanation
If unrecovered, a single unauthenticated JSON-RPC request with method `vault.publicKey.get` and no/`null` `params` field causes a runtime panic in the vault capability's gateway-message handling path on the oracle node — a denial-of-service against that node's vault capability (and potentially the whole process if the panic escapes the goroutine boundary without a `recover`). This matches CVSS AV:L/AC:L/PR:H/... in spirit but here the attacker does not even need CAP_NET_ADMIN-equivalent privilege — `MethodPublicKeyGet` is explicitly unauthenticated by design.

### Likelihood Explanation
High, if reachable: no authorization or params-presence check stands between an external client and this code path, unlike every sibling vault method, which is a strong signal of an inconsistency/oversight rather than intentional design.

### Recommendation
Add the same `if req.Params == nil { return h.errorResponse(...) }` guard used by the other vault methods at the top of `handlePublicKeyGet` (and its gateway-side counterpart in `core/services/gateway/handlers/vault/handler.go`) before dereferencing `req.Params`, returning a JSON-RPC "invalid params" error instead of unmarshalling a nil pointer.

### Proof of Concept
Send (or have the gateway forward) a JSON-RPC request such as:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
with no `params` key (or `"params": null`). Because `MethodPublicKeyGet` skips authorization and the shared params-nil check, this reaches `GatewayHandler.handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, panicking. [5](#0-4)

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-205)
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
