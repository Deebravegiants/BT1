### Title
Nil-pointer panic in Vault gateway handler when JSON-RPC request omits `params` - ([File: core/capabilities/vault/gw_handler.go])

### Summary
The Vault DON-node handler for gateway-relayed requests (`GatewayHandler.HandleGatewayMessage` in `core/capabilities/vault/gw_handler.go`) unconditionally dereferences `*req.Params` when decoding several request types (`handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`, `handlePublicKeyGet`). `Params` is an optional `*json.RawMessage` field on the JSON-RPC request and can legitimately be `nil`. An unprivileged external client can send such a request through the internet-facing Gateway HTTP endpoint, which is forwarded almost unmodified to DON nodes, causing a nil-pointer dereference panic identical in class to the TON `TrPhaseComputeVm` bug (accessing a field of a sum/optional type without checking its presence first).

### Finding Description
`GatewayHandler.HandleGatewayMessage` dispatches on `req.Method` and, for `vaulttypes.MethodPublicKeyGet`, calls `h.handlePublicKeyGet` directly with no earlier validation step: [1](#0-0) 

`handlePublicKeyGet` immediately dereferences `req.Params`: [2](#0-1) 

The same unchecked-dereference pattern exists in the other handler methods reached from `HandleGatewayMessage`: [3](#0-2) [4](#0-3) [5](#0-4) 

`req.Params` is a `*json.RawMessage` on the JSON-RPC request type, i.e. an optional field that can be `nil` if the caller omits `params` (or sends `"params": null`). Nothing in `HandleGatewayMessage` or in the earlier request-processing pipeline guarantees `Params != nil` before these handlers run, mirroring the TON bug where `ComputePh` is a sum type that must be checked before accessing the `TrPhaseComputeVm` variant.

The request reaches this node-side handler starting from an unprivileged external caller: the gateway's public HTTP endpoint decodes the raw JSON-RPC request and, for non-legacy ("new style") requests, does not require `Params` to be present before routing to the destination handler/service and forwarding to DON nodes: [6](#0-5) 

Once forwarded to the DON node, the connector's read loop invokes the registered handler's `HandleGatewayMessage` synchronously with no panic recovery: [7](#0-6) 

Because there is no `recover()` around this call, a panic in `handlePublicKeyGet` (or any of the other sibling methods) crashes the goroutine running `readLoop` for that gateway connection, stopping the node from processing any further inbound messages from that gateway — the same "observer goroutine crash" impact pattern described in the TON report.

### Impact Explanation
A single malformed/malicious JSON-RPC request (`vault.getPublicKey`, `vault.createSecrets`, etc., with `params` omitted or set to `null`) sent by any unprivileged client through the public Gateway endpoint can crash the `readLoop` goroutine that processes messages from that gateway on the DON node. This halts processing of all subsequent Vault requests (secrets creation/update/deletion/list, public key retrieval) routed through that gateway connection until the node/process is restarted or the connection is re-established, denying legitimate users' Vault operations — a concrete availability/DoS impact on a security-sensitive capability (secrets/vault management).

### Likelihood Explanation
High likelihood: no authentication or special privilege is required to reach this code path — any client capable of sending a JSON-RPC request to the public Gateway endpoint for the Vault service can omit the `params` field, and there is no schema/field-presence validation preventing this before the request is routed to `HandleGatewayMessage` and its unguarded dereferences.

### Recommendation
Add an explicit nil check for `req.Params` (returning a `UserMessageParseError` / invalid-params response) before dereferencing it in `handleSecretsCreate`, `handleSecretsUpdate`, `handleSecretsDelete`, `handleSecretsList`, and `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`. Additionally, consider wrapping `handler.HandleGatewayMessage` invocations in the connector's `readLoop` (`core/services/gateway/connector/connector.go`) with a `recover()` so a single malformed message cannot take down the entire read loop for a gateway connection.

### Proof of Concept
1. Send a JSON-RPC request to the Gateway's public HTTP endpoint targeting the Vault service, method `vault.getPublicKey` (or `vault.createSecrets`/`vault.updateSecrets`/`vault.deleteSecrets`/`vault.listSecrets`), with the `params` field omitted or explicitly `null`.
2. The Gateway (`gateway.ProcessRequest`, `core/services/gateway/gateway.go`) decodes the request and forwards it to the Vault DON node via the connector, without validating that `Params` is present.
3. On the node, `connector.readLoop` (`core/services/gateway/connector/connector.go`) calls `GatewayHandler.HandleGatewayMessage`, which routes to e.g. `handlePublicKeyGet` (`core/capabilities/vault/gw_handler.go:364-368`), executing `json.Unmarshal(*req.Params, r)` — dereferencing a nil pointer panics.
4. The panic propagates up through `readLoop`, crashing that goroutine and halting further message processing for the affected gateway connection on the node.

### Citations

**File:** core/capabilities/vault/gw_handler.go (L207-208)
```go
	case vaulttypes.MethodPublicKeyGet:
		response = h.handlePublicKeyGet(ctx, gatewayID, req)
```

**File:** core/capabilities/vault/gw_handler.go (L275-279)
```go
func (h *GatewayHandler) handleSecretsCreate(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	vaultCapRequest := vaultcommon.CreateSecretsRequest{}
	if err := json.Unmarshal(*req.Params, &vaultCapRequest); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L313-317)
```go
func (h *GatewayHandler) handleSecretsDelete(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage]) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.DeleteSecretsRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
	}
```

**File:** core/capabilities/vault/gw_handler.go (L338-342)
```go
func (h *GatewayHandler) handleSecretsList(ctx context.Context, gatewayID string, req *jsonrpc.Request[json.RawMessage], authResult *AuthResult) *jsonrpc.Response[json.RawMessage] {
	r := &vaultcommon.ListSecretIdentifiersRequest{}
	if err := json.Unmarshal(*req.Params, r); err != nil {
		return h.errorResponse(ctx, gatewayID, req, api.UserMessageParseError, err)
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

**File:** core/services/gateway/gateway.go (L221-265)
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
```

**File:** core/services/gateway/connector/connector.go (L268-298)
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
	}
```
