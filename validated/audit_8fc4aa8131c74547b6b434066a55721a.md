### Title
Unauthenticated nil pointer dereference in Vault gateway node-side `MethodPublicKeyGet` handler causes node crash - (File: `core/capabilities/vault/gw_handler.go`)

### Summary
`GatewayHandler.HandleGatewayMessage` dispatches `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` without going through `GatewayVaultRequestProcessor`, and `handlePublicKeyGet` dereferences `req.Params` without checking for `nil`, unlike every other method in this file.

### Finding Description
In `core/capabilities/vault/gw_handler.go`, `HandleGatewayMessage` routes requests by method: [1](#0-0) 

For `MethodSecretsCreate/Update/Delete/List`, requests are first passed through `h.requestProcessor.ProcessRequest`, whose per-method handlers (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`) all explicitly guard against `req.Params == nil` before unmarshaling: [2](#0-1) 

However, `MethodPublicKeyGet` bypasses this validated pipeline entirely and is handled directly by `handlePublicKeyGet`, which unconditionally dereferences `*req.Params`: [3](#0-2) 

If a JSON-RPC request for `vaulttypes.MethodPublicKeyGet` arrives with `Params == nil` (a syntactically valid JSON-RPC request that simply omits the `params` field), `*req.Params` dereferences a nil `*json.RawMessage` pointer, causing a runtime panic (nil pointer dereference) — the same root-cause bug class as the referenced ClamAV CVE-2020-3481 (crafted/malformed input triggers a null pointer dereference in a parsing routine, causing the scanning process to crash).

This message is delivered to the node process via the gateway connector's read loop, which unmarshals whatever arrives from the gateway and dispatches it straight to the registered handler: [4](#0-3) 

The gateway itself (`core/services/gateway/gateway.go`, `ProcessRequest`) only validates JSON-RPC envelope structure and request ID length for legacy requests before routing to a handler/DON — it does not enforce that `Params` is present for arbitrary JSON-RPC method calls: [5](#0-4) 

I was not able to fully trace every intermediate hop between the public-facing gateway HTTP entrypoint and the specific node-side dispatch for `MethodPublicKeyGet` in this session (in particular, confirming whether the front-end `handler.go` in `core/services/gateway/handlers/vault/` performs its own nil-params rejection for `MethodPublicKeyGet` before it is relayed to nodes, since the fetched excerpt was truncated). This should be verified before treating this as fully confirmed end-to-end from an anonymous HTTP client, but based on the code read, the node-side `GatewayHandler.handlePublicKeyGet` itself has no defense against `nil` params, which is a real gap regardless of front-end behavior (defense-in-depth failure), and any code path that forwards a raw/malformed envelope to the node (bugs in a peer gateway, a future client, or a request crafted through a different code path) will panic the node's Vault capability handler.

### Impact Explanation
A crafted `MethodPublicKeyGet` JSON-RPC request without a `params` field reaching the node's `GatewayHandler.HandleGatewayMessage` triggers a nil pointer dereference panic. Depending on Go's panic-recovery wrapping around the gateway connector's per-connection read loop, this can crash the goroutine handling gateway traffic for that node/DON member, potentially disrupting the node's participation in Vault operations — a denial-of-service condition analogous to the ClamAV null-pointer-dereference DoS.

### Likelihood Explanation
Likelihood depends on whether any earlier layer (gateway-side handler, JSON-RPC codec) rejects `MethodPublicKeyGet` requests with nil `Params` before they reach the node. Within `gw_handler.go` itself there is no such guard, and the sibling methods needed one added explicitly (`req.Params == nil` checks in `gateway_vault_request_processor.go`), indicating this was a known necessary check that was missed for `PublicKeyGet`. I could not fully verify with the available context whether an unauthenticated external actor can drive a nil-params `PublicKeyGet` request all the way to the node without an intervening check, so this should be confirmed by tracing the full front-end path in `core/services/gateway/handlers/vault/handler.go` and the JSON-RPC codec (`core/services/gateway/api/jsonrpccodec.go`).

### Recommendation
Add an explicit `if req.Params == nil { return h.errorResponse(...) }` guard at the start of `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`, consistent with the nil-checks already present in `gateway_vault_request_processor.go` for the other vault methods, so that malformed/absent `params` produce a JSON-RPC error response instead of panicking.

### Proof of Concept
Construct a JSON-RPC request forwarded to the node's Vault `GatewayHandler`:
```json
{"jsonrpc":"2.0","id":"1","method":"vault_publicKeyGet"}
```
(with `Params` field entirely omitted/nil). When this reaches `GatewayHandler.HandleGatewayMessage` and is routed to `handlePublicKeyGet`, the line `json.Unmarshal(*req.Params, r)` dereferences a nil `*json.RawMessage`, panicking the handling goroutine.

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

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L194-205)
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
```

**File:** core/services/gateway/connector/connector.go (L277-296)
```go
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
