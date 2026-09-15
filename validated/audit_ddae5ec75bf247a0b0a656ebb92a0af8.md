Audit Report

## Title
Nil pointer dereference on missing `params` in vault public-key-get gateway message handler - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` directly to `handlePublicKeyGet` without going through `GatewayVaultRequestProcessor.ProcessRequest`, which is the only place that checks `req.Params == nil` for the other vault methods. `handlePublicKeyGet` unconditionally dereferences `*req.Params` in `json.Unmarshal(*req.Params, r)`, so a request with `params` omitted or `null` causes a nil pointer dereference panic in the node's vault gateway-message handling path.

## Finding Description
`HandleGatewayMessage` routes `MethodSecretsCreate/Update/Delete/List` through `h.requestProcessor.ProcessRequest`, whose implementations (`processCreateSecretsRequest`, `processDeleteSecretsRequest`, etc.) guard with `if req.Params == nil { return ..., InvalidVaultParamsError }` before unmarshalling. [1](#0-0) [2](#0-1) 

`MethodPublicKeyGet` bypasses this and is dispatched straight to `handlePublicKeyGet`, which dereferences `req.Params` with no nil check: [3](#0-2) 

On the gateway side, `handler.HandleJSONRPCUserMessage` explicitly treats `vault.publicKey.get` as not requiring authorization ("Public key requests don't require authorization") and, when the public key is not cached, creates an active request and calls `h.handlePublicKeyGet(ctx, ar)` without validating that `req.Params` is non-nil, forwarding it on to the DON node handler above: [4](#0-3) 

I confirmed there is a generic params-nil check pattern used elsewhere for the legacy message format (`ValidatedMessageFromReq` in `core/services/gateway/handlers/common/message_util.go`, which checks `if req.Params == nil { return nil, errors.New("missing params attribute") }`), but that function is not on the vault JSON-RPC path — the vault handler operates directly on `jsonrpc.Request[json.RawMessage]` and has no equivalent guard for `MethodPublicKeyGet`. [5](#0-4) 

I was not able to locate, within the indexed content, an explicit `recover()` around the connector's dispatch to `HandleGatewayMessage` on the node side or around `HandleJSONRPCUserMessage` on the gateway side, so whether this panic crashes the whole process or is caught by an outer recover/goroutine boundary remains unconfirmed from static inspection alone — this would require checking the gateway HTTP server middleware and node connector wiring for panic recovery, which is outside what I could verify with the available tools.

## Impact Explanation
This is a legitimate correctness bug: every sibling vault method enforces `req.Params != nil` before unmarshalling, but `MethodPublicKeyGet` — the one method explicitly designed to be reachable without authorization — does not. If the panic is not recovered at a higher layer, an unauthenticated client sending `{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}` (no `params`) can crash or degrade the vault capability handling goroutine on the gateway and/or node, constituting a denial-of-service against the vault capability. This maps to an in-scope availability/DoS impact class reachable by an unprivileged actor, consistent with the reported finding.

## Likelihood Explanation
High if reachable: no authorization check and no params-presence check stand between an external, unauthenticated client and this code path on the gateway side (`HandleJSONRPCUserMessage` explicitly skips authorization for this method), and the node-side handler inherits the same unguarded pattern. The asymmetry between this method and all other vault methods (which do have the `req.Params == nil` guard) strongly indicates an oversight rather than intentional design.

## Recommendation
Add the same `if req.Params == nil { return h.errorResponse(...) }` (or equivalent `InvalidVaultParamsError`) guard at the top of `GatewayHandler.handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`, and add an analogous check in the gateway-side `handler.handlePublicKeyGet` / `HandleJSONRPCUserMessage` path in `core/services/gateway/handlers/vault/handler.go` before any `json.Unmarshal(*req.Params, ...)` dereference, returning a JSON-RPC "invalid params" error instead of panicking.

## Proof of Concept
1. Send (or have the gateway forward) a JSON-RPC request: `{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}` with no `params` key (or `"params": null`), to the gateway's vault handler endpoint.
2. Because `MethodPublicKeyGet` skips authorization in `HandleJSONRPCUserMessage` (core/services/gateway/handlers/vault/handler.go:404-420) and, when uncached, is forwarded to the node.
3. On the node, `GatewayHandler.HandleGatewayMessage` routes it directly to `handlePublicKeyGet` (core/capabilities/vault/gw_handler.go:207-208), which executes `json.Unmarshal(*req.Params, r)` at line 366 with `req.Params == nil`, causing a nil pointer dereference panic.
4. A Go unit test constructing a `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` and calling `GatewayHandler.HandleGatewayMessage` (or `handlePublicKeyGet` directly) would reproduce the panic, confirming the missing guard relative to the other vault methods' `processXRequest` functions.

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

**File:** core/services/gateway/handlers/common/message_util.go (L34-58)
```go
// ValidatedMessageFromReq validated and extracts a legacy Gateway Message
// from params field of JSON-RPC request
func ValidatedMessageFromReq(req *jsonrpc.Request[json.RawMessage]) (*api.Message, error) {
	if req.Version != "2.0" {
		return nil, errors.New("incorrect jsonrpc version")
	}
	if req.Method == "" {
		return nil, errors.New("empty method field")
	}
	if req.Params == nil {
		return nil, errors.New("missing params attribute")
	}
	var m api.Message
	err := json.Unmarshal(*req.Params, &m)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal request params: %w", err)
	}
	m.Body.Method = req.Method
	m.Body.MessageID = req.ID
	err = m.Validate()
	if err != nil {
		return nil, err
	}
	return &m, nil
}
```
