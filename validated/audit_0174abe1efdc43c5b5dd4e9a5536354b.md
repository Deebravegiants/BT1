Confirmed: `HandleJSONRPCUserMessage` at `core/services/gateway/handlers/vault/handler.go:394-420` special-cases `MethodPublicKeyGet` and forwards the raw, **unvalidated** unprivileged client request straight into `handlePublicKeyGet` / `fanOutToVaultNodes` without ever routing it through `requestProcessor.ProcessRequest`, which is the only place that checks `req.Params == nil` (in `core/capabilities/vault/gateway_vault_request_processor.go:198-231`). On the node side, `GatewayHandler.HandleGatewayMessage` (`core/capabilities/vault/gw_handler.go:207-208`) similarly calls `handlePublicKeyGet` directly for `MethodPublicKeyGet` — bypassing `ProcessRequest` entirely — and `handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go:364-368`) does `json.Unmarshal(*req.Params, r)`, dereferencing `req.Params` with no nil check.

### Title
Nil-pointer dereference panic in Vault `PublicKeyGet` path via unauthenticated client request with missing `params` - (File: core/capabilities/vault/gw_handler.go)

### Summary
An unprivileged external client can send a JSON-RPC `vault.publicKey.get` request through the internet-facing Gateway with the `params` field omitted (`null`). Unlike every other Vault method, this method bypasses the shared `GatewayVaultRequestProcessor.ProcessRequest` validation pipeline (which is the only code path that checks `req.Params == nil`), so the nil `*json.RawMessage` reaches `json.Unmarshal(*req.Params, r)` and panics on dereference.

### Finding Description
`core/services/gateway/handlers/vault/handler.go:404-419` (`HandleJSONRPCUserMessage`) explicitly carves out `vaulttypes.MethodPublicKeyGet` before the `requestProcessor.ProcessRequest` call that guards every other method, and calls `h.handlePublicKeyGet(ctx, ar)` directly on a cache miss. On the node side, `core/capabilities/vault/gw_handler.go:207-208` (`HandleGatewayMessage`) does the same: for `vaulttypes.MethodPublicKeyGet` it calls `h.handlePublicKeyGet(ctx, gatewayID, req)` directly, skipping `ProcessRequest`. `handlePublicKeyGet` at `core/capabilities/vault/gw_handler.go:364-368` then does:
```go
r := &vaultcommon.GetPublicKeyRequest{}
if err := json.Unmarshal(*req.Params, r); err != nil {
```
`req.Params` is `*json.RawMessage`; a JSON-RPC request with `"params": null` or the `params` key omitted decodes to a nil pointer for `Params`, and `*req.Params` panics with a nil pointer dereference — the exact class of bug the IoTeX report hardened against (deserialization/message handlers panicking on peer/user-controlled input). By contrast, `processCreateSecretsRequest`/`processUpdateSecretsRequest`/`processDeleteSecretsRequest`/`processListSecretIdentifiersRequest` in `core/capabilities/vault/gateway_vault_request_processor.go` all explicitly check `if req.Params == nil { return ... }` before unmarshalling — confirming this nil check is the intended/expected guard that `PublicKeyGet` is missing.

### Impact Explanation
A panic in a goroutine handling gateway/connector traffic that is not recovered will crash the Chainlink node process (or the Gateway process, depending on which side first hits the unguarded path and whether an upstream `recover()` exists in that specific call chain). This is a denial-of-service vector reachable by any unauthenticated external caller, since `PublicKeyGet` is explicitly documented as not requiring authorization ("Public key requests don't require authorization" — `handler.go:405`). A crash of a DON node or the Gateway process directly disrupts Vault availability and secret handling for all users.

### Likelihood Explanation
High. The request requires no authentication, no allowlist membership, and no valid JWT — it's the one Vault method intentionally left open to all callers. All that's required is submitting a JSON-RPC request for `vault.publicKey.get` with `params` set to `null` or omitted, an extremely low-effort attack.

### Recommendation
Add the same `req.Params == nil` guard used by the other four Vault methods (in `gateway_vault_request_processor.go`) to the `PublicKeyGet` path in both `core/services/gateway/handlers/vault/handler.go` (`HandleJSONRPCUserMessage`) and `core/capabilities/vault/gw_handler.go` (`handlePublicKeyGet`), returning a `UserMessageParseError`/`InvalidParamsError` instead of dereferencing a possibly-nil pointer. Alternatively, route `PublicKeyGet` through `ProcessRequest` (or a lightweight structural-validation helper) before unmarshalling.

### Proof of Concept
1. As an unauthenticated client, send a JSON-RPC 2.0 request to the Gateway's HTTP endpoint:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get","params":null}
```
2. On a cold cache (`h.cachedPublicKeyGetResponse == nil`), `handler.go:409-416` skips the synchronous cached-response path and calls `h.handlePublicKeyGet(ctx, ar)` → `fanOutToVaultNodes`, forwarding the request, with `params: null` intact, directly to DON nodes.
3. Each node's `GatewayHandler.HandleGatewayMessage` routes `MethodPublicKeyGet` straight to `handlePublicKeyGet` (`gw_handler.go:207-208, 364-368`), which executes `json.Unmarshal(*req.Params, r)` — dereferencing a nil `*json.RawMessage` and panicking. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-232)
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
	}
	if p.stripOwnerPrefixForAuth {
		deleteReq.RequestId = req.ID
		if err := marshalVaultParams(req, &deleteReq); err != nil {
			return nil, InvalidVaultParamsError{Method: req.Method, Err: err}
		}
	} else {
		deleteReq.RequestId = coalesceRequestID(deleteReq.RequestId, req.ID)
	}

	if err := p.validator.ValidateDeleteSecretsRequest(ctx, &deleteReq); err != nil {
		return nil, p.validationError(req, err)
	}

	return p.authorizeAndStamp(ctx, req, func(prefixedRequestID string) error {
		deleteReq.RequestId = prefixedRequestID
		vaultutils.ApplySecretIdentifierNamespaceDefaults(deleteReq.Ids)
		return marshalVaultParams(req, &deleteReq)
	})
}

func (p *GatewayVaultRequestProcessor) processListSecretIdentifiersRequest(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
) (*AuthorizedGatewayVaultRequest, error) {
	if req.Params == nil {
		return nil, InvalidVaultParamsError{Method: req.Method, Err: errors.New("request params must not be nil")}
	}
```
