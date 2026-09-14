### Title
NULL Pointer Dereference in `GatewayHandler.handlePublicKeyGet` via missing Params nil-check - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
The `MethodPublicKeyGet` handler in the node-side Vault gateway connector handler dereferences `req.Params` without checking for `nil`, unlike every other vault method (`MethodSecretsCreate`, `MethodSecretsUpdate`, `MethodSecretsDelete`, `MethodSecretsList`), which are routed through `GatewayVaultRequestProcessor` and are guarded by an explicit `if req.Params == nil` check before unmarshaling.

### Finding Description
In `HandleGatewayMessage`, the `MethodPublicKeyGet` case bypasses `GatewayVaultRequestProcessor.ProcessRequest` entirely and calls `h.handlePublicKeyGet` directly: [1](#0-0) 

`handlePublicKeyGet` then unconditionally dereferences `req.Params` (a `*json.RawMessage`) before validating it is non-nil: [2](#0-1) 

Compare this to every other vault method's processing path, which explicitly checks for a nil `Params` pointer before use, e.g. in `processDeleteSecretsRequest` and `processListSecretIdentifiersRequest`: [3](#0-2) [4](#0-3) 

Since `MethodPublicKeyGet` conceptually needs no parameters (`GetPublicKeyRequest{}` is an empty struct), a legitimate JSON-RPC 2.0 caller could omit the `params` field entirely, or an attacker could deliberately send `"params": null`. In both cases `req.Params` decodes to `nil`, and `*req.Params` in `json.Unmarshal(*req.Params, r)` dereferences a nil pointer, panicking the goroutine handling `HandleGatewayMessage`. This is directly analogous to CVE-2019-8380's root cause: a crafted/malformed input reaching a function that dereferences a pointer without a null check, causing a crash.

### Impact Explanation
`HandleGatewayMessage` is invoked by the gateway connector whenever the connected Gateway forwards a JSON-RPC request to the node for any of the registered vault methods, including `MethodPublicKeyGet`, which requires no prior authorization (it is handled outside the `authorizeAndStamp`/`Authorizer` pipeline used by the other methods). This means the public-key-get code path is reachable by unprivileged/unauthenticated callers reaching the gateway. An unhandled panic here can crash the goroutine servicing gateway messages, and — depending on whether the connector layer recovers panics at this boundary (not confirmed in the code reviewed) — could bring down the node's Vault gateway handling entirely, denying service to all legitimate vault operations (secret create/update/delete/list) for that node.

### Likelihood Explanation
High: `MethodPublicKeyGet` does not require any authentication/allowlist success and does not have a param-presence check, so any actor able to reach the gateway (which then forwards to the node) can trigger this by sending a single JSON-RPC request for this method with `params` omitted or `null`.

### Recommendation
Add an explicit nil check for `req.Params` in `handlePublicKeyGet` (mirroring the checks already present in `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest`), returning an `api.UserMessageParseError`/`InvalidVaultParamsError` response instead of dereferencing a nil pointer. Consider routing `MethodPublicKeyGet` through the same processor as other methods for consistency, or at minimum add a shared pre-check in `HandleGatewayMessage` for `req.Params == nil` before any handler dereferences it.

### Proof of Concept
1. As a gateway client, send a JSON-RPC request to the Vault gateway with method set to the value of `vaulttypes.MethodPublicKeyGet` and `"params": null` (or omit `params`).
2. The gateway forwards this to the node's `GatewayHandler.HandleGatewayMessage`.
3. Execution reaches `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` — dereferencing a nil `*json.RawMessage` — causing a runtime panic (`nil pointer dereference`). [2](#0-1)

### Citations

**File:** core/capabilities/vault/gw_handler.go (L207-211)
```go
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-200)
```go
func (p *GatewayVaultRequestProcessor) processDeleteSecretsRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L226-232)
```go
func (p *GatewayVaultRequestProcessor) processListSecretIdentifiersRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```
