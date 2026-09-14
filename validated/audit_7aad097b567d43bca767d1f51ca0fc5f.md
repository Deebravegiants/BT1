### Title
Node crash via nil pointer dereference in vault `GetPublicKey` gateway handler when `params` is null - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The `GatewayHandler.handlePublicKeyGet` function in the CRE Vault capability's node-side gateway handler dereferences `req.Params` without a nil check, unlike every sibling handler (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) which are all guarded by `req.Params == nil` checks performed in `GatewayVaultRequestProcessor` before being called. `MethodPublicKeyGet` is the one method dispatched directly, bypassing that validation pipeline entirely.

### Finding Description
In `HandleGatewayMessage`, requests are routed based on `req.Method`: [1](#0-0) 

For `MethodSecretsCreate`/`MethodSecretsUpdate`/`MethodSecretsDelete`/`MethodSecretsList`, the request is first passed through `h.requestProcessor.ProcessRequest`, whose per-method handlers (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) all explicitly check `if req.Params == nil` and return a typed `InvalidVaultParamsError` before any `json.Unmarshal(*req.Params, ...)` occurs: [2](#0-1) 

However, `MethodPublicKeyGet` is dispatched directly to `handlePublicKeyGet` with no such validation: [3](#0-2) [4](#0-3) 

`json.Unmarshal(*req.Params, r)` directly dereferences the `*json.RawMessage` pointer. If a caller sends a JSON-RPC request for `vault_getPublicKey` (per `vaulttypes.MethodPublicKeyGet`) with `params` omitted or explicitly `null`, `req.Params` decodes to a nil pointer and the dereference `*req.Params` panics with a nil pointer dereference. This is the same bug class as the referenced p11-kit CVE-2026-2100: a caller-controlled null parameter is dereferenced by the request-handling layer without a null check, before any authorization/validation gate is reached.

This handler runs on the node side, invoked whenever a Gateway forwards an inbound message to the node via `GatewayConnectorHandler.HandleGatewayMessage`; no attacker-controlled parameter is validated for nil before this call for this specific method, and unlike the Create/Update/Delete/List paths there is no authorization step (`authResult`) required either — `MethodPublicKeyGet` is processed before any auth pipeline runs.

### Impact Explanation
A panic inside `HandleGatewayMessage` that is not recovered will propagate up through the connector's message-processing goroutine. Depending on whether the caller of this handler wraps handler invocation in a `recover()` (not found in the connector code reviewed), this can crash the node process or terminate the goroutine servicing gateway messages, disrupting the node's ability to process Vault (and potentially other) gateway traffic — an availability impact consistent with the CVSS vector of the referenced CVE (`A:L`, no confidentiality/integrity impact). Because `GetPublicKey` requires no authentication/authorization before reaching the vulnerable unmarshal call, this is reachable by any unprivileged caller able to reach the Gateway's vault service endpoint.

### Likelihood Explanation
High. Triggering the bug only requires sending a single JSON-RPC request with method `vault_getPublicKey` (`vaulttypes.MethodPublicKeyGet`) and `params` set to `null` or omitted. No valid credentials, encryption keys, or prior state are needed since this code path executes before any authorization pipeline (`requestProcessor.ProcessRequest`) is invoked.

### Recommendation
Add an explicit `if req.Params == nil` guard at the start of `handlePublicKeyGet` (mirroring the pattern already used in `processCreateSecretsRequest`, `processUpdateSecretsRequest`, etc.), returning `h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))` instead of unmarshaling a nil pointer. Consider also routing `MethodPublicKeyGet` through a shared nil-check helper (e.g. `vaultutils.InspectJSONRPCParams`, which already performs this check) to prevent recurrence for future methods added to this dispatch switch.

### Proof of Concept
1. As an unauthenticated/unprivileged external client, send a Gateway user-facing request that resolves to the Vault service's `HandleGatewayMessage`, with body:
```json
{
  "jsonrpc": "2.0",
  "id": "poc-1",
  "method": "vault_getPublicKey"
}
```
(i.e., omit `params`, or set `"params": null`.)
2. On the node side, `GatewayHandler.HandleGatewayMessage` routes to `handlePublicKeyGet` since `req.Method == vaulttypes.MethodPublicKeyGet`. [3](#0-2) 
3. `handlePublicKeyGet` executes `json.Unmarshal(*req.Params, r)` where `req.Params` is `nil`, causing a nil pointer dereference panic. [5](#0-4)

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
