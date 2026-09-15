### Title
Unauthenticated nil-pointer panic in `GatewayHandler.handlePublicKeyGet` due to missing `req.Params` nil check - (File: core/capabilities/vault/gw_handler.go)

### Summary
The node-side vault gateway-connector handler, `GatewayHandler.HandleGatewayMessage`, dispatches `vault_publicKeyGet` (`vaulttypes.MethodPublicKeyGet`) requests directly to `handlePublicKeyGet` without going through the shared `GatewayVaultRequestProcessor` pipeline that all other vault methods use. `handlePublicKeyGet` unconditionally dereferences `*req.Params` before checking it for `nil`, exactly matching the root-cause pattern in the reported kin-openapi advisory: a legally-reachable, unauthenticated code path that dereferences an optional field without a nil guard, causing a panic.

### Finding Description
In `core/capabilities/vault/gw_handler.go`, `HandleGatewayMessage` special-cases `MethodPublicKeyGet` to bypass the normal validation pipeline: [1](#0-0) 

For every other vault method (`MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, `MethodSecretsList`), the request is routed through `h.requestProcessor.ProcessRequest`, whose per-method handlers in `gateway_vault_request_processor.go` explicitly check `req.Params == nil` and return a structured `InvalidVaultParamsError` before any unmarshal occurs, e.g.: [2](#0-1) 

`MethodPublicKeyGet`, however, skips that pipeline entirely and goes straight to: [3](#0-2) 

`json.Unmarshal(*req.Params, r)` dereferences `req.Params` with no preceding nil check. If `req.Params` is `nil` — which is a legitimate, protocol-legal JSON-RPC request shape, and is in fact treated as valid for this exact method by the sibling gateway-side handler's test (`TestVaultHandler_PublicKeyGet` constructs and successfully processes a `MethodPublicKeyGet` request with `Params: nil`) — this line panics with a nil-pointer dereference: [4](#0-3) 

This mirrors the kin-openapi bug class precisely: other sibling code paths (`mt == nil` guard in kin-openapi; `req.Params == nil` guard in the sibling `processDeleteSecretsRequest`/`processListSecretIdentifiersRequest`) demonstrate the author's intent to guard against this exact nil case, but one reachable, legal branch (`content` media type with no schema; `MethodPublicKeyGet` bypassing the processor) omits the guard and dereferences unconditionally.

### Impact Explanation
`HandleGatewayMessage` is the `connector.GatewayConnectorHandler` entry point invoked by the gateway connector whenever it relays a JSON-RPC message from the internet-facing gateway to a node. `MethodPublicKeyGet` requires no owner/session authorization (it returns a DON-wide public key, not user-scoped data), so this path is reachable by any unauthenticated client able to submit a `vault_publicKeyGet` request through the gateway with a missing/empty `params` field. A crash here takes down request handling on the affected node process for that gateway connection (denial of service), consistent with the CWE-476/DoS classification of the analog report. The severity ceiling matches the analog's Medium (`A:L`/`A:H`)-class impact: the blast radius is a node-side panic, not fund movement, key disclosure, or auth bypass.

### Likelihood Explanation
High for reachability: `MethodPublicKeyGet` is dispatched with zero request validation in `HandleGatewayMessage` (no `req.Params == nil` guard, no `requestProcessor.ProcessRequest` call), and the sibling gateway-side handler's own test suite demonstrates that a `nil`-`Params` request for this exact method is considered a normal, non-error input. Whether the gateway-facing ingress additionally strips or rejects nil-params `vault_publicKeyGet` requests before they reach the node connector could not be fully confirmed from the indexed portion of `core/services/gateway/handlers/vault/handler.go`'s forwarding logic; this is the primary remaining uncertainty.

### Recommendation
Add a `req.Params == nil` guard at the top of `GatewayHandler.handlePublicKeyGet` (and ideally route `MethodPublicKeyGet` through the same `requestProcessor`-style validation as the other vault methods for consistency), mirroring the existing guards in `processDeleteSecretsRequest` / `processListSecretIdentifiersRequest`:
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	if req.Params == nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))
	}
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		...
```

### Proof of Concept
1. Construct a JSON-RPC request with `Method: vaulttypes.MethodPublicKeyGet` and `Params: nil` (a legal request shape, as validated by the existing `TestVaultHandler_PublicKeyGet`-style test fixtures which use `Params: nil` for this method).
2. Deliver it to the node via the gateway connector so it reaches `GatewayHandler.HandleGatewayMessage`.
3. `HandleGatewayMessage` dispatches straight to `handlePublicKeyGet` (no processor call for this method) [5](#0-4) .
4. `handlePublicKeyGet` executes `json.Unmarshal(*req.Params, r)` [6](#0-5) , dereferencing the nil `*json.RawMessage`, producing a runtime nil-pointer-dereference panic on the node.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L200-211)
```go
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
