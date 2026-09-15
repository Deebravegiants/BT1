## Finding

The chainlink CMS/OpenSSL analog exists in the Vault capability's gateway message handler.

### Title
NULL Pointer Dereference via Unchecked `req.Params` in Vault `handlePublicKeyGet` - (File: core/capabilities/vault/gw_handler.go)

### Summary
When a `GatewayHandler` receives a JSON-RPC request for `vaulttypes.MethodPublicKeyGet`, it dispatches directly to `handlePublicKeyGet` without any prior `nil`-check on `req.Params`, unlike every other Vault method which validates `req.Params == nil` before dereferencing it.

### Finding Description
In `HandleGatewayMessage`, all other request types (`MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, `MethodSecretsList`) are routed through `GatewayVaultRequestProcessor.ProcessRequest`, whose per-method handlers (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) each explicitly check `if req.Params == nil` before unmarshalling [1](#0-0) , [2](#0-1) , [3](#0-2) .

However, `MethodPublicKeyGet` bypasses this validation path entirely and is dispatched straight to `h.handlePublicKeyGet(ctx, gatewayID, req)`: [4](#0-3) .

`handlePublicKeyGet` unconditionally dereferences `req.Params` (`json.Unmarshal(*req.Params, r)`) with no `nil` guard: [5](#0-4) .

If an attacker-supplied JSON-RPC request for method `public_key.get` (or whatever `vaulttypes.MethodPublicKeyGet` resolves to) is sent through the connector with `Params` omitted (a valid JSON-RPC request has no required `params` field), `req.Params` is `nil`, and `*req.Params` is a nil pointer dereference on a `*json.RawMessage`, causing an immediate panic in the node process handling the gateway message — directly analogous to the CVE's pattern of examining an optional field (`KeyEncryptionAlgorithmIdentifier.parameters`) without checking for its presence before dereferencing it.

### Impact Explanation
A panic inside `HandleGatewayMessage` crashes the goroutine processing gateway messages. Since Vault's gateway handler is a long-lived service (`GatewayHandler` implements `connector.GatewayConnectorHandler`) invoked per inbound gateway message, an unhandled panic here can crash or destabilize the node process, resulting in denial of service for the Vault capability (and potentially the node) before any authentication or authorization logic (`Authorizer`, allowlist, JWT checks) is reached — because `MethodPublicKeyGet` performs no authorization at all in this handler.

### Likelihood Explanation
This method is reachable from any actor able to submit a message through the gateway connector addressed to the Vault handler's method set (`vaulttypes.Methods` includes `MethodPublicKeyGet`), requiring only a syntactically valid JSON-RPC request lacking `params`. No cryptographic material, prior session, or elevated privilege is needed to trigger it, making the likelihood high for a network-reachable/gateway-reachable attacker.

### Recommendation
Add an explicit `if req.Params == nil` check at the top of `handlePublicKeyGet` (mirroring the checks already present in `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest`) and return a proper `api.UserMessageParseError`/`InvalidVaultParamsError` response instead of dereferencing a nil pointer. Consider auditing all other gateway/JSON-RPC message handlers across the codebase for the same unguarded `*req.Params` dereference pattern.

### Proof of Concept
Send a JSON-RPC request via the gateway connector to a node running the Vault capability with:
```json
{"jsonrpc":"2.0","id":"1","method":"<vaulttypes.MethodPublicKeyGet value>"}
```
(omitting the `params` field entirely). `HandleGatewayMessage` routes this to `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` where `req.Params` is `nil`, causing a nil-pointer dereference panic [5](#0-4) .

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L115-117)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L157-159)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L198-200)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
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
