This confirms the full end-to-end path. The gateway-side `handler.HandleJSONRPCUserMessage` in `core/services/gateway/handlers/vault/handler.go` explicitly special-cases `vaulttypes.MethodPublicKeyGet` to skip all authorization/param validation ("Public key requests don't require authorization") and forwards the raw request — including a `nil` `Params` — straight to `h.handlePublicKeyGet(ctx, ar)`, which calls `fanOutToVaultNodes`, which calls `h.don.SendToNode(ctx, node.Address, &ar.req)` with the original (possibly nil-`Params`) request unmodified. [1](#0-0) [2](#0-1) [3](#0-2) 

The existing test `TestVaultHandler_PublicKeyGet` even constructs `jsonRequest` with `Params: nil` and successfully drives it through `handlePublicKeyGet` → `fanOutToVaultNodes` → `don.SendToNode`, proving that a nil-`Params` `PublicKeyGet` request is a normal, accepted code path at the gateway with no rejection. [4](#0-3) 

On the node side, `GatewayHandler.HandleGatewayMessage` routes `MethodPublicKeyGet` directly to `handlePublicKeyGet` without going through `GatewayVaultRequestProcessor`'s nil-checks, and `handlePublicKeyGet` unconditionally dereferences `*req.Params`: [5](#0-4) [6](#0-5) 

This closes the gap the original report flagged as unverified: an unauthenticated/unprivileged HTTP client can submit `{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}` (no `params` field) to the gateway's public vault endpoint, and the gateway forwards it to the node's `GatewayHandler`, whose `handlePublicKeyGet` panics on `*req.Params`.

Audit Report

## Title
Unauthenticated nil pointer dereference in Vault gateway node-side `MethodPublicKeyGet` handler causes node crash - (File: `core/capabilities/vault/gw_handler.go`)

## Summary
The gateway-side vault `handler.HandleJSONRPCUserMessage` treats `vaulttypes.MethodPublicKeyGet` as a request that "doesn't require authorization" and forwards it to nodes without any params validation, unlike every other vault method which goes through `GatewayVaultRequestProcessor`'s nil-checks. On the node side, `GatewayHandler.HandleGatewayMessage` dispatches `MethodPublicKeyGet` directly to `handlePublicKeyGet`, which unconditionally dereferences `*req.Params`, causing a nil pointer dereference panic when an unprivileged client sends a `vault.publicKey.get` request with no `params` field.

## Finding Description
At the gateway's public-facing entrypoint, `handler.HandleJSONRPCUserMessage` special-cases `MethodPublicKeyGet`, bypassing `requestProcessor.ProcessRequest` (and its nil-`Params` guards) entirely, and forwards the request as-is to `handlePublicKeyGet` → `fanOutToVaultNodes` → `don.SendToNode(ctx, node.Address, &ar.req)`, sending the original request object — including a nil `Params` — unmodified to every DON member node. On the node side, `GatewayHandler.HandleGatewayMessage` routes `MethodPublicKeyGet` straight to `handlePublicKeyGet` (bypassing `GatewayVaultRequestProcessor`, whose sibling methods `processCreateSecretsRequest`/`processUpdateSecretsRequest`/`processDeleteSecretsRequest`/`processListSecretIdentifiersRequest` all explicitly check `req.Params == nil` before unmarshaling). `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go` does `json.Unmarshal(*req.Params, r)` without any nil check, so a nil `Params` pointer is dereferenced, panicking the goroutine handling gateway messages for that node.

The existing unit test `TestVaultHandler_PublicKeyGet` demonstrates that a request with `Params: nil` is a normal, accepted input at the gateway layer and is forwarded to nodes via `SendToNode`, confirming there is no earlier validation layer that rejects this input before it reaches the vulnerable node-side code.

## Impact Explanation
An unauthenticated/unprivileged HTTP client sending a minimal JSON-RPC request (`{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}` with no `params`) to the vault gateway causes that request to be relayed to every node in the DON, where `GatewayHandler.handlePublicKeyGet` panics on nil pointer dereference. This is a denial-of-service vulnerability affecting the Vault capability's gateway message-handling goroutine on potentially all DON member nodes simultaneously, since the gateway fans the request out to all `donConfig.Members`.

## Likelihood Explanation
This requires no authentication, no special role, and no prior state — it is a single, syntactically minimal JSON-RPC request over the vault gateway's public HTTP endpoint. The gateway-side handler explicitly documents that `PublicKeyGet` requests "don't require authorization," and the code path from HTTP request to node-side panic is fully traceable through `handler.go` and `gw_handler.go` with no intervening nil-params check, and is directly reproducible via the existing test harness pattern used in `TestVaultHandler_PublicKeyGet`.

## Recommendation
Add an explicit `if req.Params == nil { return h.errorResponse(...) }` guard at the start of `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`, consistent with the nil-checks already present in `gateway_vault_request_processor.go` for the other vault methods, so that malformed/absent `params` produce a JSON-RPC error response instead of panicking. Consider also validating params at the gateway-side `handler.HandleJSONRPCUserMessage` before forwarding `MethodPublicKeyGet` requests to nodes, for defense-in-depth.

## Proof of Concept
1. Send an HTTP request to the vault gateway's public endpoint with body:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
(no `params` field, hence `Params == nil` after decoding).
2. The gateway's `handler.HandleJSONRPCUserMessage` (core/services/gateway/handlers/vault/handler.go:404-420) takes the `MethodPublicKeyGet` branch, skipping `requestProcessor.ProcessRequest`, and forwards the request via `fanOutToVaultNodes` → `don.SendToNode` to all DON member nodes.
3. On each node, `GatewayHandler.HandleGatewayMessage` (core/capabilities/vault/gw_handler.go:207-208) routes to `handlePublicKeyGet` (line 364-368), which executes `json.Unmarshal(*req.Params, r)`, dereferencing a nil `*json.RawMessage` and panicking the handling goroutine.
4. A Go unit test analogous to `TestVaultHandler_PublicKeyGet` in `handler_test.go` (lines 1272-1317), but constructing `req.Params = nil` and invoking `GatewayHandler.HandleGatewayMessage` directly (or `handlePublicKeyGet` on `core/capabilities/vault/gw_handler.go`), reproduces the panic.

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

**File:** core/services/gateway/handlers/vault/handler.go (L736-744)
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
```

**File:** core/services/gateway/handlers/vault/handler_test.go (L1289-1317)
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
```

**File:** core/capabilities/vault/gw_handler.go (L207-208)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
```

**File:** core/capabilities/vault/gw_handler.go (L364-368)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```
