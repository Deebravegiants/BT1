## Analysis

The CVE describes a NULL-pointer-dereference crash triggered by crafted input reaching a message-parsing routine. The closest reachable analog in this codebase is in the Vault capability's Gateway-to-node message handler.

### Title
Nil pointer dereference in `vault.publicKey.get` handling crashes the node - ([File: core/capabilities/vault/gw_handler.go])

### Summary
`GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without going through the `requestProcessor.ProcessRequest` pipeline that other methods use, and without checking whether `req.Params` is nil before dereferencing it.

### Finding Description
In `core/capabilities/vault/gw_handler.go`, the switch in `HandleGatewayMessage` routes `vaulttypes.MethodSecretsCreate/Update/Delete/List` through `h.requestProcessor.ProcessRequest`, which validates and authorizes the request. `vaulttypes.MethodPublicKeyGet` instead calls `h.handlePublicKeyGet(ctx, gatewayID, req)` directly: [1](#0-0) 

`handlePublicKeyGet` unconditionally dereferences `req.Params`: [2](#0-1) 

`req.Params` is typed `*json.RawMessage` on the JSON-RPC request and is `nil` whenever a JSON-RPC request omits the `params` field. Every other handler in this file (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`) has the exact same unguarded `*req.Params` pattern, but those are reached only after `ProcessRequest`'s validation step; `handlePublicKeyGet` is reached with no such gate.

This handler is invoked from `GatewayHandler.HandleGatewayMessage`, which is called by `gatewayConnector.readLoop` for every JSON-RPC message the node's Gateway connector receives from a Gateway: [3](#0-2) 

The message content originates from an unprivileged HTTP caller hitting the internet-facing `gateway.ProcessRequest` entry point, which decodes the raw JSON-RPC envelope and forwards it, by method name, to the registered node handler with no requirement that `params` be present: [4](#0-3) 

`readLoop` runs as a dedicated per-gateway goroutine with no `recover()` around the handler invocation, so a panic there is not contained by Gin's `gin.Recovery()` middleware (that middleware only guards HTTP handlers on the Gateway process, not the node's connector goroutine).

### Impact Explanation
A panic in an unrecovered goroutine terminates the entire Go process. Since this handler runs inside the Chainlink node process (not the Gateway process), a crafted `vault.publicKey.get` request with a missing/null `params` field — sent by any client capable of reaching the Gateway's public HTTP endpoint — can crash the node, causing a denial of service. This matches the CVE's bug class: a NULL/nil pointer dereference triggered by crafted input in a parsing routine, without requiring elevated privileges.

### Likelihood Explanation
`MethodPublicKeyGet` is explicitly designed to bypass authorization (see the `authResult = nil` path and the missing `ProcessRequest` call for this method), so no valid JWT/allowlist entry is required to reach it. Triggering the bug requires only sending a JSON-RPC request with `method: "vault.publicKey.get"` and no `params` field (or `params: null`) to a Gateway configured to route to a node running this handler.

### Recommendation
Add an explicit nil check for `req.Params` in `handlePublicKeyGet` (and, defensively, in the other `handleSecrets*` functions) before dereferencing, returning a `UserMessageParseError`/`InvalidParamsError` response instead of panicking — mirroring the "request params must not be nil" checks already present in `core/capabilities/vault/authorizer.go`'s `validateSecretOwnersMatchAuthorized`. Additionally, wrap `readLoop`'s handler invocation in `connector.go` with a `recover()` so a bug in any single handler cannot take down the whole node process.

### Proof of Concept
Send a JSON-RPC message to the Gateway with no `params`:
```json
{"jsonrpc":"2.0","id":"1","method":"vault.publicKey.get"}
```
The Gateway relays this to the node's `VaultHandler` via `HandleGatewayMessage`; the switch routes it to `handlePublicKeyGet`, which executes `json.Unmarshal(*req.Params, r)` with `req.Params == nil`, causing a nil pointer dereference panic in the connector's `readLoop` goroutine. [5](#0-4) [2](#0-1) [6](#0-5)

### Citations

**File:** core/capabilities/vault/gw_handler.go (L180-211)
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

**File:** core/services/gateway/connector/connector.go (L268-296)
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
```

**File:** core/services/gateway/gateway.go (L220-253)
```go
// Called by the server
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
```
