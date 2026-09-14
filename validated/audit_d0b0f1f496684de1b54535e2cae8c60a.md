### Title
Null Pointer Dereference in Vault Gateway Handler via `vault_publicKeyGet` with missing params - ([File: core/capabilities/vault/gw_handler.go])

### Summary
Every other gateway-routed vault JSON-RPC method (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`) is routed through `GatewayVaultRequestProcessor.processRequest`, which explicitly checks `if req.Params == nil` before dereferencing [1](#0-0) , [2](#0-1) , [3](#0-2) . The `MethodPublicKeyGet` branch, however, bypasses this processor entirely and calls `handlePublicKeyGet` directly, which unconditionally dereferences `*req.Params` with no nil check.

### Finding Description
In `HandleGatewayMessage`, the switch on `req.Method` routes `vaulttypes.MethodPublicKeyGet` straight to `h.handlePublicKeyGet(ctx, gatewayID, req)` without any call into `h.requestProcessor.ProcessRequest`: [4](#0-3) .

`handlePublicKeyGet` then does:
```go
r := &vaultcommon.GetPublicKeyRequest{}
if err := json.Unmarshal(*req.Params, r); err != nil {
``` [5](#0-4) 

If `req.Params` is `nil` (i.e., the JSON-RPC request omits the `params` field, which is legal per JSON-RPC 2.0 for parameterless calls), `*req.Params` dereferences a nil pointer, causing a runtime panic. This mirrors the PX4 bug class exactly: a CLI/RPC entry point that is normally guarded by an argument/parameter presence check in sibling code paths, but one specific command handler skips that check and dereferences the missing value directly, crashing the process.

The dereference happens on the node side (`GatewayHandler` implements `connector.GatewayConnectorHandler` and is invoked from `readLoop` in the gateway connector whenever a message with method `vault_publicKeyGet` arrives from the Gateway) — i.e., it is reachable by any client able to reach the Gateway's user-facing endpoint and send a `vault_publicKeyGet` request with no `params`, without needing prior authentication/authorization, since `MethodPublicKeyGet` is explicitly excluded from the authorizer/validator pipeline (`requestProcessor.ProcessRequest`) that all other vault methods go through.

### Impact Explanation
An unauthenticated/unprivileged actor able to send messages through the Gateway to a DON member's Vault capability can crash the node process (denial of service) by sending a `vault_publicKeyGet` JSON-RPC request with a missing/null `params` field. Since Go panics from a nil pointer dereference in a request-handling goroutine will, depending on how the connector's read loop recovers panics, either crash the node process or at minimum terminate the connector's message-processing goroutine, disrupting the node's Vault/gateway connectivity. This matches the "VA:H" (availability impact) characterization of the CVE analog. There is no confidentiality or integrity impact — this is a crash-only bug.

### Likelihood Explanation
High likelihood of triggerability: the request requires no authentication, no valid secrets, and no specific node state — an empty/missing `params` field in a `vault_publicKeyGet` request is trivial to construct and send through the Gateway's public-facing message path.

### Recommendation
Add an explicit nil check for `req.Params` at the start of `handlePublicKeyGet` (mirroring the pattern already used in `GatewayVaultRequestProcessor.process*Request` methods), returning a `UserMessageParseError`/`InvalidParamsError` response instead of dereferencing directly:
```go
func (h *GatewayHandler) handlePublicKeyGet(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	if req.Params == nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, errors.New("request params must not be nil"))
	}
	...
```
Consider also auditing all other direct `*req.Params` dereferences in `gw_handler.go` (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) to confirm they are unreachable with nil params only because `ProcessRequest` guarantees non-nil params upstream, and add defensive checks if that invariant is ever violated by a refactor.

### Proof of Concept
1. As an unprivileged client with access to the Gateway's user-facing JSON-RPC endpoint, send:
```json
{"jsonrpc":"2.0","id":"1","method":"vault_publicKeyGet"}
```
(note: no `"params"` field, or `"params": null`)
2. The Gateway forwards this message unmodified to the DON node's `GatewayHandler.HandleGatewayMessage`.
3. `req.Method == vaulttypes.MethodPublicKeyGet` routes to `handlePublicKeyGet` with `req.Params == nil` [4](#0-3) .
4. `json.Unmarshal(*req.Params, r)` dereferences the nil `*json.RawMessage`, panicking the goroutine handling the gateway message [5](#0-4) .

### Citations

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L115-117)
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L230-232)
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
