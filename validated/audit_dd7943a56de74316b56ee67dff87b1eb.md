Audit Report

## Title
Unauthenticated NULL Pointer Dereference in Vault `MethodPublicKeyGet` Handling via Missing Params Nil-Check - (File: core/capabilities/vault/gw_handler.go)

## Summary
The gateway-side vault handler treats `vaulttypes.MethodPublicKeyGet` as an unauthenticated, unvalidated request and forwards it to DON nodes without ever running it through `GatewayVaultRequestProcessor.ProcessRequest`, which is the only place a `req.Params == nil` guard exists for vault methods. The node-side `GatewayHandler.handlePublicKeyGet` then unconditionally executes `json.Unmarshal(*req.Params, r)`, causing a nil pointer dereference panic if `req.Params` is nil.

## Finding Description
In `core/services/gateway/handlers/vault/handler.go`, `HandleJSONRPCUserMessage` special-cases `MethodPublicKeyGet` before the `IsGatewaySecretsMethod` check and before `h.requestProcessor.ProcessRequest` is invoked: [1](#0-0) 
This path calls `h.newActiveRequest(req, callback)` and `h.handlePublicKeyGet(ctx, ar)` directly, passing along the raw, attacker-controlled `req` (with its original `Params`, which can be `nil` or omitted by an external client) — unlike `MethodSecretsCreate/Update/Delete/List`, which go through `h.requestProcessor.ProcessRequest` (only reached later in the function, at line 427): [2](#0-1) 

On the node side, `GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go` dispatches `MethodPublicKeyGet` directly to `handlePublicKeyGet`, bypassing `requestProcessor.ProcessRequest` entirely (that processor is only invoked for `SecretsCreate/Update/Delete/List`): [3](#0-2) 
`handlePublicKeyGet` then dereferences the pointer with no nil check: [4](#0-3) 

This is confirmed by comparing to `GatewayVaultRequestProcessor`, whose `processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, and `processListSecretIdentifiersRequest` all begin with an explicit `if req.Params == nil` check before unmarshaling — but `MethodPublicKeyGet` never runs through this shared processor at all, on either the gateway or node side: [5](#0-4) [6](#0-5) 

The finding's code citations and control-flow description are accurate as verified directly against the repository.

## Impact Explanation
A nil pointer dereference in `json.Unmarshal(*req.Params, r)` panics the goroutine handling `HandleGatewayMessage` on the node side. Since `gatewayConnector` handlers are invoked per-message from the gateway connector, and Go panics propagate up the call stack unless recovered, this can crash the node process or terminate the connector's read loop, denying service to the vault capability for that node. Because `MethodPublicKeyGet` is explicitly exempted from authorization ("Public key requests don't require authorization"), no credentials, allowlisting, or workflow ownership is required to reach this code path — any external client with access to the gateway's public JSON-RPC endpoint can trigger it. This maps to an in-scope denial-of-service/availability impact against DON node vault processing.

## Likelihood Explanation
High. The only precondition is that the gateway's local public-key cache is empty (e.g., shortly after startup, or after cache expiry — `defaultPublicKeyGetCacheDurationSeconds = 300`), which forces the gateway to forward the request to nodes rather than serving it from cache. An unprivileged client can then simply send a `vault_publicKeyGet` JSON-RPC request with `params` omitted or `null`. No authentication, no valid ciphertext, and no special timing beyond an empty cache window is needed. This is trivially repeatable.

## Recommendation
Add an explicit `if req.Params == nil` check in `handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go`, before line 366) before dereferencing, returning a `UserMessageParseError`/`InvalidParamsError` response instead of panicking. Optionally also validate `req.Params` on the gateway side in `HandleJSONRPCUserMessage`'s `MethodPublicKeyGet` branch before forwarding to nodes, for defense in depth and to avoid needlessly propagating malformed requests to the DON.

## Proof of Concept
1. Ensure the gateway's cached public key is empty (fresh gateway startup, before `fetchVaultPublicKey`'s periodic ticker populates the cache, or after cache expiry).
2. Send a JSON-RPC request to the gateway's public HTTP endpoint for the vault DON:
```json
{"jsonrpc":"2.0","id":"1","method":"vault_publicKeyGet"}
```
with no `params` field (or `"params": null`).
3. `HandleJSONRPCUserMessage` sees `cachedPublicKey == nil`, creates an `activeRequest` from the raw `req` (with nil `Params`), and calls `h.handlePublicKeyGet(ctx, ar)`, which forwards the request to DON nodes unmodified.
4. On the node, `GatewayHandler.HandleGatewayMessage` routes `MethodPublicKeyGet` straight to `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` on a nil `req.Params`, panicking the goroutine.
5. A minimal Go unit test constructing a `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and invoking `GatewayHandler.HandleGatewayMessage` directly (or `handlePublicKeyGet`) would reproduce the panic deterministically without needing network access.

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

**File:** core/services/gateway/handlers/vault/handler.go (L422-434)
```go
	if !vaulttypes.IsGatewaySecretsMethod(req.Method) {
		return h.sendImmediateUserResponse(ctx, req, callback, api.UnsupportedMethodError, errors.New("this method is unsupported: "+req.Method))
	}

	_, cachedPublicKey := h.getCachedPublicKey()
	authorized, err := h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)
	if err != nil {
		if vaultcap.IsInvalidVaultParamsError(err) {
			return h.sendImmediateUserResponse(ctx, req, callback, api.InvalidParamsError, err)
		}
		h.lggr.Errorw("request not authorized", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "error", err)
		return errors.New("request not authorized: " + err.Error())
	}
```

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L91-108)
```go
func (p *GatewayVaultRequestProcessor) processRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	publicKey *tdh2easy.PublicKey,
) (*AuthorizedGatewayVaultRequest, error) {
	switch req.Method {
	case vaulttypes.MethodSecretsCreate:
		return p.processCreateSecretsRequest(ctx, req, publicKey)
	case vaulttypes.MethodSecretsUpdate:
		return p.processUpdateSecretsRequest(ctx, req, publicKey)
	case vaulttypes.MethodSecretsDelete:
		return p.processDeleteSecretsRequest(ctx, req)
	case vaulttypes.MethodSecretsList:
		return p.processListSecretIdentifiersRequest(ctx, req)
	default:
		return nil, fmt.Errorf("unsupported gateway vault method: %s", req.Method)
	}
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
