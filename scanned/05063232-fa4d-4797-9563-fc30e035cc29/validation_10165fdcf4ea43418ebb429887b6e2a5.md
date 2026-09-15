## Analysis

Confirmed root cause: `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go` unmarshal-dereferences `req.Params` without a nil check, and it is reachable via the node-side `HandleGatewayMessage` dispatch for `MethodPublicKeyGet` without going through `GatewayVaultRequestProcessor.ProcessRequest` (which is the only place that enforces the "params must not be nil" check for the other vault methods).

### Title
Nil Pointer Dereference in Vault `GetPublicKey` Handler via Missing Params on Gateway-Forwarded Request - (File: core/capabilities/vault/gw_handler.go)

### Summary
The node-side Vault gateway handler dereferences `req.Params` unconditionally in `handlePublicKeyGet`, while the sibling secrets methods (`SecretsCreate`, `SecretsUpdate`, `SecretsDelete`, `SecretsList`) are routed through `GatewayVaultRequestProcessor.ProcessRequest`, which explicitly checks `req.Params == nil` before use. `MethodPublicKeyGet` bypasses that processor entirely.

### Finding Description
In `HandleGatewayMessage` [1](#0-0) , the `MethodPublicKeyGet` case is dispatched directly to `h.handlePublicKeyGet(ctx, gatewayID, req)` without any pre-validation of `req.Params`, unlike `MethodSecretsCreate/Update/Delete/List`, which go through `h.requestProcessor.ProcessRequest`.

`handlePublicKeyGet` then does:
```go
r := &vaultcommon.GetPublicKeyRequest{}
if err := json.Unmarshal(*req.Params, r); err != nil { ... }
``` [2](#0-1) 

If `req.Params` is `nil`, `*req.Params` dereferences a nil pointer, causing a runtime panic.

By contrast, every other secrets-related processing path in `GatewayVaultRequestProcessor` (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) explicitly guards against this:
```go
if req.Params == nil {
    return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
}
``` [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

This is analogous to the CVE-2021-39516 bug class: a decoder/handler dereferences attacker-influenced input without a null check, causing a crash (DoS) rather than memory corruption.

The path is reachable from an unprivileged external caller: the gateway's public HTTP-facing vault handler explicitly documents that `MethodPublicKeyGet` "doesn't require authorization" and is processed "right away," fetching from nodes on a cache miss [7](#0-6) . This request/params can be forwarded to the DON's node-side `GatewayHandler.HandleGatewayMessage`, which crashes if `Params` is nil (e.g., a JSON-RPC request omitting the `params` field entirely, which is legal per JSON-RPC 2.0).

### Impact Explanation
A crafted, unauthenticated JSON-RPC request for `vault_getPublicKey` with `params` omitted (nil) — sent to the Gateway and forwarded to a node — causes a nil-pointer-dereference panic in the node's `GatewayHandler.HandleGatewayMessage` goroutine. Depending on panic recovery at the connector layer, this can crash or destabilize the node process, denying service to the vault capability (and potentially the whole node if not isolated by a recover()). This matches CVSS AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H — availability impact via DoS, no confidentiality/integrity impact.

### Likelihood Explanation
High. `MethodPublicKeyGet` is explicitly documented as not requiring authorization, is the first case checked in `HandleJSONRPCUserMessage` [7](#0-6) , and omitting `params` in a JSON-RPC 2.0 request is trivial and standards-compliant. No authentication, allowlist entry, or capability access is required to trigger the crash path once the request reaches a node that has a cache miss.

### Recommendation
Add an explicit `req.Params == nil` check in `handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go`) before dereferencing, mirroring the pattern already used in `GatewayVaultRequestProcessor`'s other methods, returning a `UserMessageParseError`/`InvalidVaultParamsError`-style response instead of unmarshalling a nil pointer. Consider unifying `MethodPublicKeyGet` handling through the same processor validation path used by the other vault methods to avoid this divergence recurring.

### Proof of Concept
1. Send a JSON-RPC 2.0 request to the Gateway's vault endpoint with `method: "vault_getPublicKey"` and no `params` field (or `params: null`), and an ID that forces a cache miss (or issue it before the gateway's public-key cache is warm).
2. The Gateway forwards this to a DON node without validating `params` for this method (per `handler.go`'s comment that this method "doesn't require authorization" and is processed immediately).
3. On the node, `GatewayHandler.HandleGatewayMessage` dispatches directly to `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, causing a nil pointer dereference panic. [2](#0-1)

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-212)
```go
func (h *GatewayHandler) HandleGatewayMessage(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) (err error) {
	reqLggr := h.requestLogger(req, gatewayID)
	reqLggr.Debugw("received message from gateway", "req", req)

	var response *jsonrpc.Response[json.RawMessage]
	var authResult *AuthResult

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L230-232)
```go
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-419)
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
```
