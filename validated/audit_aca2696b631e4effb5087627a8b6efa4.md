### Title
Nil pointer dereference in `GatewayHandler.handlePublicKeyGet` via missing `params` in `vault.publicKey.get` request - (File: core/capabilities/vault/gw_handler.go)

### Summary
The node-side vault gateway handler dereferences `req.Params` without a nil check for the `vault.publicKey.get` method, unlike every other vault method which is routed through `GatewayVaultRequestProcessor` (which does check `req.Params == nil`). An unprivileged client can send a JSON-RPC request omitting the `params` field, and it will be forwarded from the gateway to the node's `GatewayHandler.HandleGatewayMessage`, resulting in a nil pointer dereference panic.

### Finding Description
`GatewayHandler.HandleGatewayMessage` dispatches by method. For `MethodSecretsCreate/Update/Delete/List`, it always runs `h.requestProcessor.ProcessRequest(...)`, and `GatewayVaultRequestProcessor`'s per-method handlers (e.g. `processCreateSecretsRequest`) explicitly guard `if req.Params == nil { return ... }` before dereferencing. [1](#0-0) 

However, `MethodPublicKeyGet` bypasses this pipeline entirely and is dispatched directly: [2](#0-1) 

`handlePublicKeyGet` immediately dereferences `*req.Params` with no nil check: [3](#0-2) 

Since `req.Params` is a `*json.RawMessage`, if the wire request omits `"params"` (or is unmarshaled without it), the field stays `nil`, and `*req.Params` panics with "invalid memory address or nil pointer dereference" before `json.Unmarshal` is even invoked — the same bug class as GPAC's `gf_isom_get_media_data_size()` NULL pointer dereference from unvalidated/missing input.

This request originates from an unprivileged user: the public gateway entrypoint `HandleJSONRPCUserMessage` for `MethodPublicKeyGet` forwards the request directly to nodes without enforcing a non-nil `params` field on the JSON-RPC envelope (that generic validation does not exist for JSON-RPC-style, non-legacy requests in `gateway.ProcessRequest`). [4](#0-3) 

I was unable to fully trace, within the available context, whether the node-side connector/websocket read loop that invokes `HandleGatewayMessage` wraps each message dispatch with a `recover()` (a grep for `recover()` under `core/services/gateway/**` and `core/capabilities/vault/**` found no relevant guard around this call path, but I could not fully inspect `core/services/gateway/connector/connector.go`'s message-processing goroutine to confirm whether such a panic would crash the node process or just the handling goroutine).

### Impact Explanation
If unrecovered, the panic crashes the goroutine (or process) handling gateway-forwarded requests on the Chainlink node, denying availability of the node's vault capability handling — matching the CVE's impact profile (`C:N/I:N/A:H`, availability-only). This is a legitimate unprivileged-actor DoS analog reachable via the internet-facing gateway.

### Likelihood Explanation
High: the trigger requires only omitting or nulling the `params` field of a standard `vault.publicKey.get` JSON-RPC request — no authentication bypass or special access is needed, since `MethodPublicKeyGet` explicitly does not require authorization ("Public key requests don't require authorization"). [5](#0-4) 

### Recommendation
Add a `req.Params == nil` guard at the top of `handlePublicKeyGet` (mirroring the pattern used in `GatewayVaultRequestProcessor`'s other handlers) and return a `UserMessageParseError` response instead of dereferencing the pointer directly.

### Proof of Concept
1. Send a JSON-RPC request to the public gateway HTTP endpoint targeting the vault service with method `vault.publicKey.get` and no `params` field (or `"params": null`):
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
2. The gateway's `handler.HandleJSONRPCUserMessage` forwards this to the node's `GatewayHandler.HandleGatewayMessage` since `MethodPublicKeyGet` requires no authorization pipeline.
3. On the node, `handlePublicKeyGet` executes `json.Unmarshal(*req.Params, r)`, dereferencing the nil `*json.RawMessage` and panicking.

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

**File:** core/services/gateway/gateway.go (L267-276)
```go
	startTime := time.Now()
	var method string
	callback := handlerscommon.NewCallback()
	if isLegacyRequest {
		method = msg.Body.Method
		err = h.HandleLegacyUserMessage(ctx, msg, callback)
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L404-409)
```go
	if req.Method == vaulttypes.MethodPublicKeyGet {
		// Public key requests don't require authorization,
		// Let's process this request right away.
		// Note we cache this value quite aggressively so don't need to worry about DoS.
		publicKeyResponseBytes, cachedPublicKey := h.getCachedPublicKey()
		if cachedPublicKey == nil {
```
