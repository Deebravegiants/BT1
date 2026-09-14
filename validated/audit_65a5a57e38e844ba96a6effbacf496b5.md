### Title
Unauthenticated null-pointer dereference (DoS) in Vault gateway handler `PublicKeyGet` path via nil `params` - (File: core/capabilities/vault/gw_handler.go)

### Summary
`GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without going through `GatewayVaultRequestProcessor.ProcessRequest`, which is the only place in this pipeline that checks `req.Params == nil` before dereferencing. `handlePublicKeyGet` unmarshal-dereferences `*req.Params` unconditionally, so a caller can trigger a nil-pointer dereference/panic simply by sending a `vault.publicKey.get` JSON-RPC message with no `params` field.

### Finding Description
In `HandleGatewayMessage`, the dispatch switch is: [1](#0-0) 

For `MethodSecretsCreate/Update/Delete/List`, requests are always routed through `h.requestProcessor.ProcessRequest`, which calls into `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest` — every one of which explicitly guards `if req.Params == nil { return ... InvalidVaultParamsError }` before touching `*req.Params`: [2](#0-1) [3](#0-2) 

However, `MethodPublicKeyGet` bypasses `ProcessRequest`/`requestProcessor` entirely and goes straight to `handlePublicKeyGet`, which has no such nil check and unconditionally dereferences the params pointer: [4](#0-3) 

Line 366 (`json.Unmarshal(*req.Params, r)`) dereferences a `*json.RawMessage` that is nil whenever the inbound JSON-RPC request omits (or sets `null` for) the `params` field. This is analogous in bug class to CVE-2022-34682 (unprivileged actor triggers a null-pointer dereference in a privileged/kernel component, causing denial of service) — here the "privileged component" is the node-side Vault gateway handler that any gateway-routed caller (including unprivileged/unauthenticated requesters, since this method is dispatched before any `Authorizer`/JWT check) can reach.

### Impact Explanation
A panic inside `HandleGatewayMessage` — invoked from the gateway connector's inbound message-processing path for every DON node running the Vault capability — is a denial of service against that node's Vault handling for the process (and, depending on how the connector processes messages, potentially crashes the whole node process if not isolated via a per-message `recover()`). This impacts availability of node Vault services and, if the process crashes, disrupts other node functions that share that process (chainlink node binary hosts multiple services). No confidentiality or integrity impact is implicated by the null dereference itself, matching the CVSS profile of the source CVE (`C:N/I:N/A:H`).

### Likelihood Explanation
This is trivially reachable: `MethodPublicKeyGet` is not authorization/JWT-gated in `HandleGatewayMessage` (it's the only method that produces a `response` outside the code branches that call `h.requestProcessor.ProcessRequest`/`getMasterPublicKey`+auth), and constructing a JSON-RPC request with `method: "vault.publicKey.get"` and no `params` field requires no privileges, valid signature-only routing through the gateway, or workflow ownership. This is a very low-effort, high-reliability trigger.

### Recommendation
Add an explicit `req.Params == nil` guard at the top of `handlePublicKeyGet` (mirroring the pattern already used in `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest`), returning `api.UserMessageParseError` via `h.errorResponse` instead of dereferencing a nil pointer. Additionally, consider wrapping the `HandleGatewayMessage` dispatch (or its per-method handlers) in a `recover()` at the connector boundary so that any future missed nil-check or malformed-input panic in a single request cannot escalate to crash the entire node process.

### Proof of Concept
Send (via a client/node reachable by the gateway connector) a JSON-RPC message to the node's Vault `GatewayHandler`:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "vault.publicKey.get"
}
```
i.e., omit the `params` field entirely (or set it to `null`). This causes `req.Params` to be `nil` (`*json.RawMessage`), and `handlePublicKeyGet`'s `json.Unmarshal(*req.Params, r)` at [5](#0-4)  dereferences the nil pointer, panicking inside `HandleGatewayMessage`.

Note: I was unable to fully verify, within the available tool budget, whether the gateway connector's message-receive loop wraps each `HandleGatewayMessage`/handler invocation in a `recover()` (I found no such guard in `core/services/gateway/connector/connector.go` via search, but did not read the full file), so the exact blast radius (single request failure vs. full node-process crash) is not conclusively confirmed here.

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

**File:** core/capabilities/vault/gw_handler.go (L364-386)
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.GetPublicKeyRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}

	resp, err := h.secretsService.GetPublicKey(ctx, r)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.HandlerError, fmt.Errorf("failed to get public key: %w", err))
	}

	b, err := json.Marshal(resp)
	if err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.NodeReponseEncodingError, err)
	}

	return &jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      req.ID,
		Method:  req.Method,
		Result:  (*json.RawMessage)(&b),
	}
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
