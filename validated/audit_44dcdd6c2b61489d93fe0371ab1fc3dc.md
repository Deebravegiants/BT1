Audit Report

## Title
Nil pointer dereference in `GatewayHandler.handlePublicKeyGet` via missing `params` in `vault.publicKey.get` request - (File: core/capabilities/vault/gw_handler.go)

## Summary
The node-side vault gateway handler dereferences `req.Params` without a nil check for the `vault.publicKey.get` method, unlike every other vault method routed through `GatewayVaultRequestProcessor`, which explicitly checks `req.Params == nil` before use. An unprivileged client can send a `vault.publicKey.get` JSON-RPC request with no (or null) `params` field through the public gateway, which is forwarded to the node without authorization checks, causing a nil pointer dereference panic on the node.

## Finding Description
`GatewayHandler.HandleGatewayMessage` dispatches `MethodSecretsCreate/Update/Delete/List` through `h.requestProcessor.ProcessRequest(...)`, and the corresponding handlers in `GatewayVaultRequestProcessor` (e.g. `processCreateSecretsRequest`) explicitly guard against nil params: [1](#0-0) 

`MethodPublicKeyGet`, however, is dispatched directly to `handlePublicKeyGet`, bypassing that validated pipeline entirely: [2](#0-1) 

`handlePublicKeyGet` immediately dereferences `*req.Params` with no nil check, unlike its sibling handlers such as `handleSecretsDelete`/`handleSecretsList`, which are only reached after the guarded `ProcessRequest` call: [3](#0-2) 

On the gateway side, `HandleJSONRPCUserMessage` explicitly special-cases `MethodPublicKeyGet` to skip the authorization/validation pipeline ("Public key requests don't require authorization") and forwards it straight to `h.handlePublicKeyGet(ctx, ar)`, whereas all other vault methods go through `h.requestProcessor.ProcessRequest(ctx, &req, cachedPublicKey)`, which performs its own params validation: [4](#0-3) [5](#0-4) 

Since `req.Params` is `*json.RawMessage`, an incoming JSON-RPC request omitting the `params` field (or with `"params": null`) leaves this field `nil` throughout the chain, and `*req.Params` at line 366 of `gw_handler.go` panics with a nil pointer dereference before any parsing or validation occurs. I searched for `recover()` guards in `core/services/gateway/**` and found no relevant match, and none in `core/services/gateway/connector/**` either, so nothing intercepts this panic within the reviewed code paths.

## Impact Explanation
An unrecovered panic in the goroutine handling gateway-forwarded messages constitutes an availability-impacting bug (denial of service) affecting the node's vault capability handling, consistent with the Chainlink bounty program's DoS/availability impact class. This is in-scope as it is triggerable by an unprivileged client hitting the internet-facing gateway without any special role or credential.

## Likelihood Explanation
High. The trigger is a standard, minimal `vault.publicKey.get` JSON-RPC request with the `params` field omitted or null — the gateway code explicitly documents that this method "doesn't require authorization," so no authentication or role escalation is needed to reach the vulnerable code path.

## Recommendation
Add a `req.Params == nil` guard at the top of `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`, mirroring the pattern in `GatewayVaultRequestProcessor`'s handlers, returning a `UserMessageParseError`/`InvalidParamsError` response instead of dereferencing the pointer directly. Additionally, consider validating `params` presence generically for JSON-RPC-style requests at the gateway ingress (`gateway.ProcessRequest`) as defense-in-depth, and add a `recover()` around per-message handler dispatch in the gateway connector's message loop.

## Proof of Concept
1. Send an HTTP request to the public gateway endpoint targeting the vault handler with:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
(no `params` field, or `"params": null`).
2. `handler.HandleJSONRPCUserMessage` (core/services/gateway/handlers/vault/handler.go:404-419) special-cases `MethodPublicKeyGet`, skips the `ProcessRequest` validation pipeline, and (on cache miss) calls `h.handlePublicKeyGet(ctx, ar)`, forwarding the request to a node via `HandleGatewayMessage`.
3. On the node, `GatewayHandler.HandleGatewayMessage` routes to `handlePublicKeyGet` (core/capabilities/vault/gw_handler.go:207-208, 364-368), which executes `json.Unmarshal(*req.Params, r)` — dereferencing the nil `*json.RawMessage` and panicking with "invalid memory address or nil pointer dereference."
4. A minimal Go unit test invoking `GatewayHandler.HandleGatewayMessage` directly with a `*jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` reproduces the panic deterministically.

### Citations

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
