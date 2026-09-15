Based on my review, the finding is confirmed valid.

Audit Report

## Title
Nil pointer dereference in vault `GatewayHandler.handlePublicKeyGet` via unchecked `*req.Params` - (File: `core/capabilities/vault/gw_handler.go`)

## Summary
The node-side `GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet`, bypassing the `requestProcessor.ProcessRequest` pipeline that explicitly checks `req.Params == nil` for the create/update/delete/list methods. `handlePublicKeyGet` unconditionally dereferences `*req.Params` in `json.Unmarshal(*req.Params, r)`, which panics if `req.Params` is `nil`. This is reachable from an unprivileged client because the gateway-side handler (`core/services/gateway/handlers/vault/handler.go`) treats `MethodPublicKeyGet` as not requiring authorization and forwards the user's raw request (`&ar.req`, including its `Params` field as received) unchanged to DON nodes via `fanOutToVaultNodes` → `h.don.SendToNode`, with no nil-params check anywhere on that path.

## Finding Description
On the node side, `HandleGatewayMessage` dispatches by method: `MethodSecretsCreate/Update` and `MethodSecretsDelete/List` go through `h.requestProcessor.ProcessRequest`, whose per-method handlers (`processCreateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) all explicitly guard `if req.Params == nil { return ... }` before calling `json.Unmarshal(*req.Params, ...)`. [1](#0-0) [2](#0-1) 

`MethodPublicKeyGet`, however, goes straight to `handlePublicKeyGet`, which has no such guard and dereferences the pointer immediately: [3](#0-2) 

On the gateway side, `HandleJSONRPCUserMessage` special-cases `MethodPublicKeyGet` as not requiring authorization, and if the cached public key is absent, forwards the request unchanged to nodes without any nil-params validation: [4](#0-3) 

The gateway's own `handlePublicKeyGet` (a different function, on the gateway relay, not the node) simply calls `fanOutToVaultNodes`, which forwards `&ar.req` — the raw incoming request including its original `Params` — to every DON node without modification or a nil check: [5](#0-4) [6](#0-5) 

I confirmed there is no nil-params guard anywhere in `core/services/gateway/handlers/vault/handler.go` for the `MethodPublicKeyGet` path (the only `InvalidVaultParamsError`/nil-params references in that file are in a test, not in the production code path for this method). A repo unit test even demonstrates the intended-and-tested pattern of sending `Params: nil` for `MethodPublicKeyGet` through `handlePublicKeyGet`/`HandleJSONRPCUserMessage` at the gateway level, confirming a nil `Params` for this method is accepted at the gateway and forwarded as-is to nodes: [7](#0-6) 

Since `vaultcommon.GetPublicKeyRequest` carries no required fields, a legitimate/unprivileged client naturally has no reason to include a `params` field at all, and nothing in the JSON-RPC decode/validation path for this method enforces its presence before the request is forwarded from the gateway to the node's `HandleGatewayMessage`, where `handlePublicKeyGet` panics on `*req.Params`.

## Impact Explanation
A nil pointer dereference in `handlePublicKeyGet` on the node side panics the goroutine processing the gateway message. Depending on whether panic recovery isolates individual `HandleGatewayMessage` invocations, this can crash the node process or at minimum disrupt vault processing for that node, denying vault public-key retrieval and potentially other in-flight vault operations. This is a Denial of Service impact, an in-scope class for Chainlink bounty triage given it's exploitable by an unauthenticated/unprivileged actor sending a normal-looking JSON-RPC request to the public gateway endpoint (no operator, admin, or host access required, and no auth check bypass needed since this method is explicitly exempted from authorization).

## Likelihood Explanation
The path is fully reachable by an unprivileged client: `MethodPublicKeyGet` is explicitly exempted from the `requestProcessor.ProcessRequest` authorization/validation pipeline on both the gateway (`core/services/gateway/handlers/vault/handler.go:404-419`) and node (`core/capabilities/vault/gw_handler.go:207-208`) sides, and the gateway forwards the raw `Params` field of the incoming HTTP JSON-RPC request unchanged to DON nodes. An attacker only needs to send an HTTP POST to the vault gateway endpoint with `"method": "vault.publicKey.get"` and `"params": null` (or omitted), which is a trivially malformed-but-plausible request compared to the documented usage shown in test/system-test code, which always sets `Params: &vault_helpers.GetPublicKeyRequest{}`.

## Recommendation
Add an explicit nil-params guard at the top of `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`, mirroring the pattern used in `gateway_vault_request_processor.go`'s other handlers, e.g.:
```go
if req.Params == nil {
    return h.errorResponse(ctx, gatewayID, req, api.InvalidParamsError, errors.New("request params must not be nil"))
}
```
Additionally, consider validating/normalizing `Params` for `MethodPublicKeyGet` at the gateway ingress (`core/services/gateway/handlers/vault/handler.go`) before forwarding to nodes, to fail fast with a clean JSON-RPC error rather than relying on nodes to individually guard against nil.

## Proof of Concept
1. Send an HTTP POST to the vault gateway endpoint with a JSON-RPC body: `{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}` (no `params` field, or `"params": null`), when the gateway has no cached public key yet (e.g., freshly started gateway/DON, or use `wg_handler` cache eviction/timing).
2. The gateway's `HandleJSONRPCUserMessage` sees `cachedPublicKey == nil`, creates an active request via `newActiveRequest(req, callback)` retaining `Params == nil`, and calls `handlePublicKeyGet` → `fanOutToVaultNodes`, which sends `&ar.req` unmodified to every DON node.
3. On each node, `GatewayHandler.HandleGatewayMessage` routes `MethodPublicKeyGet` straight to `handlePublicKeyGet(ctx, gatewayID, req)`, which executes `json.Unmarshal(*req.Params, r)` and panics with a nil pointer dereference since `req.Params == nil`.
4. This can be reproduced as a Go unit test analogous to `TestVaultHandler_PublicKeyGet` in `core/services/gateway/handlers/vault/handler_test.go` (which already exercises `Params: nil` at the gateway relay level) but calling `core/capabilities/vault/gw_handler.go`'s `GatewayHandler.HandleGatewayMessage` / `handlePublicKeyGet` directly with a `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and asserting it panics instead of returning a graceful `InvalidParamsError` response.

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L110-121)
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
```

**File:** core/services/gateway/handlers/vault/handler.go (L394-420)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
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

**File:** core/services/gateway/handlers/vault/handler.go (L692-708)
```go
func (h *handler) handlePublicKeyGet(ctx context.Context, ar *activeRequest) error {
	l := logger.With(h.lggr, "method", ar.req.Method, "requestID", ar.req.ID)

	publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
	if cachedPublicKey != nil {
		l.Debugw("returning cached public key response")
		return h.sendSuccessResponse(ctx, l, ar, &jsonrpc.Response[json.RawMessage]{
			Version: jsonrpc.JsonRpcVersion,
			ID:      ar.req.ID,
			Method:  ar.req.Method,
			Result:  (*json.RawMessage)(&publicKeyResponseBytes),
		})
	}

	l.Debugw("cache stale: forwarding request to nodes", "now", h.clock.Now())
	return h.fanOutToVaultNodes(ctx, l, ar)
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L1289-1336)
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

	_, pk, _, err := tdh2easy.GenerateKeys(1, 3)
	require.NoError(t, err)
	pkBytes, err := pk.Marshal()
	require.NoError(t, err)
	publicKey := hex.EncodeToString(pkBytes)
	responseData := &vaultcommon.GetPublicKeyResponse{
		PublicKey: publicKey,
	}
	resultBytes, err := json.Marshal(responseData)
	require.NoError(t, err)
	response := jsonrpc.Response[json.RawMessage]{
		ID:     "request_id",
		Method: vaulttypes.MethodPublicKeyGet,
		Result: (*json.RawMessage)(&resultBytes),
	}
	for n := range 2*mcr.F + 1 {
		err = h.HandleNodeMessage(t.Context(), &response, fmt.Sprintf("0xnode%d", n))
		require.NoError(t, err)
	}

	resp, err := callback.Wait(t.Context())
	require.NoError(t, err)
	var publicKeyResponse jsonrpc.Response[vaultcommon.GetPublicKeyResponse]
	err = json.Unmarshal(resp.RawResponse, &publicKeyResponse)
	require.NoError(t, err)

	assert.Equal(t, jsonRequest.ID, publicKeyResponse.ID, "request ID should match")
	assert.Equal(t, publicKey, publicKeyResponse.Result.PublicKey, "public key should match")

	// Now let's make HandleJSONRPCUserMessage request, it'll have been cached due to the previous call.
	callback = common.NewCallback()
	jsonRequest = jsonrpc.Request[json.RawMessage]{
		ID:     "another_request_id",
		Method: vaulttypes.MethodPublicKeyGet,
		Params: nil,
	}
	err = h.HandleJSONRPCUserMessage(t.Context(), jsonRequest, callback)
	require.NoError(t, err)
```
