Audit Report

## Title
Nil-pointer dereference (panic/DoS) on unauthenticated `vault.publicKeyGet` gateway message - ([File: core/capabilities/vault/gw_handler.go])

## Summary
`GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go` routes `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without passing through `GatewayVaultRequestProcessor` (used for all other vault methods) and without checking `req.Params == nil`. `handlePublicKeyGet` unconditionally executes `json.Unmarshal(*req.Params, r)`, which panics on a nil `*json.RawMessage` if `Params` is omitted from the JSON-RPC envelope.

## Finding Description
`HandleGatewayMessage` dispatches based on `req.Method`: for `MethodSecretsCreate/Update/Delete/List` it always goes through `h.requestProcessor.ProcessRequest`, whose per-method processors explicitly check `if req.Params == nil { return ... InvalidVaultParamsError }` (e.g. `processDeleteSecretsRequest`) before unmarshalling. [1](#0-0) [2](#0-1) 

`MethodPublicKeyGet`, however, bypasses this pipeline entirely and calls `handlePublicKeyGet` directly: [3](#0-2) 

`handlePublicKeyGet` immediately dereferences `*req.Params`: [4](#0-3) 

I traced the full request path to confirm the request actually reaches this node-side code with a nil `Params` field, since the claim needs an unauthenticated, unprivileged entry point:

1. An external HTTP caller sends a JSON-RPC request to the gateway's `ProcessRequest`, which decodes the raw bytes into `jsonrpc.Request[json.RawMessage]` and dispatches it to the relevant handler's `HandleJSONRPCUserMessage`. [5](#0-4) 
2. The gateway-side vault handler `HandleJSONRPCUserMessage` (`core/services/gateway/handlers/vault/handler.go`) special-cases `vaulttypes.MethodPublicKeyGet` and explicitly skips authorization/validation ("Public key requests don't require authorization... Let's process this request right away"), forwarding straight to `handlePublicKeyGet` → `fanOutToVaultNodes`, which sends the **original, unvalidated** `ar.req` (the user's raw request, including a possibly-nil `Params`) to every DON node via `h.don.SendToNode`. [6](#0-5) [7](#0-6) 
3. On the node side, the gateway connector's `readLoop` unmarshals the incoming bytes into `jsonrpc.Request[json.RawMessage]` and calls `handler.HandleGatewayMessage(ctx, ..., &req)` synchronously in the read loop, with no recover/panic-guard visible around this call. [8](#0-7) 
4. This reaches `GatewayHandler.HandleGatewayMessage` → `handlePublicKeyGet`, which dereferences the nil `*req.Params`.

Nothing in this path enforces that `Params` is non-nil for `MethodPublicKeyGet` before it reaches the node-side dereference — the gateway-side handler explicitly opts this method out of `requestProcessor.ProcessRequest`, and the node-side handler also skips it. The other vault methods are protected because their processors in `gateway_vault_request_processor.go` explicitly check `req.Params == nil` before unmarshalling.

## Impact Explanation
This is a genuine, code-confirmed denial-of-service bug: an unauthenticated caller can craft a JSON-RPC request with `method: "vault.publicKeyGet"` and no `params` field, causing the request to flow — unauthenticated and unvalidated — through the gateway to every node in the DON, where `handlePublicKeyGet` panics on the nil dereference. Because the panic occurs inside the connector's synchronous `readLoop` (no visible `recover()`), this can crash the goroutine handling gateway messages for that connection, and in Go, an unrecovered panic in any goroutine terminates the entire process — so this is a real node crash/DoS vector reachable without any credentials, role, or valid vault ciphertext. This maps to an in-scope "unauthorized action leading to node DoS" style impact via the gateway request path.

## Likelihood Explanation
High. The trigger requires only a syntactically valid JSON-RPC envelope with `method` set to `vault.publicKeyGet` and `params` omitted, sent to the gateway's public HTTP endpoint — no authentication, no allowlist entry, and no valid vault key material needed, since the gateway-side handler explicitly treats this method as not requiring authorization and forwards the raw request to nodes unchanged.

## Recommendation
Add an explicit `req.Params == nil` check in `handlePublicKeyGet` (both gateway-side and node-side) before calling `json.Unmarshal(*req.Params, r)`, returning `api.UserMessageParseError`/`InvalidVaultParamsError` instead of panicking — mirroring the guards already present in `processCreateSecretsRequest`, `processDeleteSecretsRequest`, etc. Additionally, consider adding panic recovery around `HandleGatewayMessage` dispatch in the connector's `readLoop` as defense-in-depth, since an unrecovered panic there can crash the node process regardless of the specific root cause.

## Proof of Concept
Send an HTTP JSON-RPC request to the gateway's vault-service endpoint:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "vault.publicKeyGet"
}
```
with no `params` field (or `"params": null`) and no cached public key on the gateway (i.e., `cachedPublicKeyGetResponse == nil`, which is the default state before the periodic refresh populates it, or reachable by targeting a fresh gateway/handler instance). This causes:
1. `handler.HandleJSONRPCUserMessage` (gateway) to skip authorization for `MethodPublicKeyGet` and forward the raw request to nodes via `fanOutToVaultNodes` (`core/services/gateway/handlers/vault/handler.go:404-420`, `736-744`).
2. The node's `connector.go` `readLoop` to unmarshal the message and call `handler.HandleGatewayMessage` (`core/services/gateway/connector/connector.go:268-297`).
3. `GatewayHandler.HandleGatewayMessage` to route to `handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go:207-208`), which executes `json.Unmarshal(*req.Params, r)` (`core/capabilities/vault/gw_handler.go:364-368`), dereferencing the nil `*json.RawMessage` and panicking.

A Go unit test invoking `GatewayHandler.HandleGatewayMessage` directly with a `jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` would deterministically reproduce the panic and serves as the most direct regression test.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L200-206)
```go
	case vaulttypes.MethodSecretsDelete, vaulttypes.MethodSecretsList:
		authorized, pipelineErr := h.requestProcessor.ProcessRequest(ctx, req, nil)
		if pipelineErr != nil {
			response = h.gatewayErrorResponse(ctx, gatewayID, req, pipelineErr)
			break
		}
		authResult = authorized.AuthResult
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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-204)
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
```

**File:** core/services/gateway/gateway.go (L221-276)
```go
func (g *gateway) ProcessRequest(ctx context.Context, rawRequest []byte, auth string) (rawResponse []byte, httpStatusCode int) {
	// decode
	jsonRequest, err := jsonrpc2.DecodeRequest[json.RawMessage](rawRequest, auth)
	if err != nil {
		return newError("", api.UserMessageParseError, err.Error())
	}
	msg, err := g.codec.DecodeJSONRequest(jsonRequest)
	if err != nil {
		return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
	}
	if len(jsonRequest.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return newError(jsonRequest.ID, api.UserMessageParseError, "request ID is too long: "+strconv.Itoa(len(jsonRequest.ID))+". max is 200 characters")
	}
	isLegacyRequest := false
	var h handlers.Handler
	var handlerKey string
	if msg == nil || msg.Body.DonID == "" {
		serviceName := jsonRequest.ServiceName()
		if handler, ok := g.serviceToMultiHandler[serviceName]; ok {
			h = handler
			handlerKey = serviceName
		} else if donID, ok := g.serviceNameToDonID[serviceName]; ok {
			// Fallback to legacy service name -> DON ID mapping
			if handler, ok := g.handlers[donID]; ok {
				h = handler
				handlerKey = donID
			}
		}
		if h == nil {
			return newError(jsonRequest.ID, api.HandlerError, "Service name not found: "+serviceName)
		}
	} else {
		// Legacy request with DON ID - validate and fetch handler
		isLegacyRequest = true
		if err = msg.Validate(); err != nil {
			return newError(jsonRequest.ID, api.UserMessageParseError, err.Error())
		}
		handlerKey = msg.Body.DonID
		var ok bool
		h, ok = g.handlers[handlerKey]
		if !ok {
			return newError(jsonRequest.ID, api.UnsupportedDONIdError, "Unsupported DON ID: "+handlerKey)
		}
	}

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

**File:** core/services/gateway/handlers/vault/handler.go (L736-744)
```go
func (h *handler) fanOutToVaultNodes(ctx context.Context, l logger.Logger, ar *activeRequest) error {
	var nodeErrors []error
	for _, node := range h.donConfig.Members {
		err := h.don.SendToNode(ctx, node.Address, &ar.req)
		if err != nil {
			nodeErrors = append(nodeErrors, err)
			l.Errorw("error sending request to node", "node", node.Address, "error", err)
		}
	}
```

**File:** core/services/gateway/connector/connector.go (L268-297)
```go
func (c *gatewayConnector) readLoop(gatewayState *gatewayState) {
	defer c.closeWait.Done()
	ctx, cancel := c.shutdownCh.NewCtx()
	defer cancel()

	for {
		select {
		case <-c.shutdownCh:
			return
		case item := <-gatewayState.conn.ReadChannel():
			var req jsonrpc.Request[json.RawMessage]
			err := json.Unmarshal(item.Data, &req)
			if err != nil {
				c.lggr.Errorw("parse error when reading from Gateway", "id", gatewayState.config.ID, "err", err)
				break
			}
			c.handlersMu.RLock()
			handler, exists := c.handlers[req.Method]
			c.handlersMu.RUnlock()
			if !exists {
				c.lggr.Errorw("no handler for method", "id", gatewayState.config.ID, "method", req.Method)
				break
			}
			// do not break on error. HandleGatewayMessage handles errors
			// by sending a response back to the Gateway.
			err = handler.HandleGatewayMessage(ctx, gatewayState.config.ID, &req)
			if err != nil {
				c.lggr.Warnw("failed to handle message from Gateway", "id", gatewayState.config.ID, "method", req.Method, "err", err)
			}
		}
```
