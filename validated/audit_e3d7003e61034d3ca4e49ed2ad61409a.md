### Title
Nil-pointer dereference (panic/DoS) on unauthenticated `vault.publicKeyGet` gateway message - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without going through the shared `GatewayVaultRequestProcessor` pipeline that all other vault methods use, and without any authorization step. `handlePublicKeyGet` then dereferences `*req.Params` unconditionally, causing a nil-pointer panic if `Params` is omitted/null in the JSON-RPC envelope.

### Finding Description
In `core/capabilities/vault/gw_handler.go`, `HandleGatewayMessage` switches on `req.Method`: [1](#0-0) 

For `MethodSecretsCreate/Update/Delete/List`, the request is first passed through `h.requestProcessor.ProcessRequest`, whose per-method processors (`processCreateSecretsRequest`, `processDeleteSecretsRequest`, etc.) explicitly guard `if req.Params == nil { return ... InvalidVaultParamsError }` before ever unmarshalling: [2](#0-1) 

However, `MethodPublicKeyGet` skips this pipeline entirely and calls `handlePublicKeyGet` unconditionally, with no authorization and no nil check on `req.Params`: [3](#0-2) 

`handlePublicKeyGet` immediately dereferences `*req.Params`: [4](#0-3) 

If a gateway-relayed JSON-RPC message with `method: "vault.publicKeyGet"` omits the `params` field (or sends `"params": null`), `req.Params` is a nil `*json.RawMessage`, and `*req.Params` panics with a nil-pointer dereference — structurally identical to the ICC `IccTagLut.cpp` bug class (member/dereference access through a null pointer of externally-influenced type) referenced in CVE-2026-34552.

### Impact Explanation
This code runs in the node-side gateway connector handler (`GatewayHandler`), which processes messages that the gateway relays from external, unauthenticated HTTP callers. Since `MethodPublicKeyGet` bypasses both the shared authorization step and the `Params == nil` guard applied to every other vault method, any external caller able to reach the gateway's vault endpoint with a `vault.publicKeyGet` method and a missing/null `params` field can trigger a panic in the node process handling gateway messages, resulting in denial of service to the node's vault-handling goroutine/service.

### Likelihood Explanation
High: the trigger requires only sending a syntactically valid JSON-RPC envelope with `method` set to `vault.publicKeyGet` and `params` omitted — no authentication, no valid vault ciphertext, and no allowlist entry needed, since this method is dispatched before any authorization is applied.

### Recommendation
Add an explicit `req.Params == nil` check (mirroring the other vault method processors) in `handlePublicKeyGet` (and any other gateway/node handler that dereferences `*req.Params` without validation) before calling `json.Unmarshal(*req.Params, r)`, returning an `api.UserMessageParseError`/`InvalidVaultParamsError` response instead of panicking. Recover from panics at the top of `HandleGatewayMessage` is a defense-in-depth complement but does not fix the underlying missing validation.

### Proof of Concept
Send (via the gateway, or directly to the node's gateway connector inbound handler) a JSON-RPC message:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "vault.publicKeyGet"
}
```
with no `params` field. `HandleGatewayMessage` routes this to `handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go:207-208`), which executes `json.Unmarshal(*req.Params, r)` (`core/capabilities/vault/gw_handler.go:366`) — dereferencing the nil `*json.RawMessage` pointer and panicking.

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
