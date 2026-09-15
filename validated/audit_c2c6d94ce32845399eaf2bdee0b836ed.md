Audit Report

## Title
Missing nil-check on `req.Params` in Vault node-side `handlePublicKeyGet` causes nil pointer dereference panic - (File: `core/capabilities/vault/gw_handler.go`)

## Summary
`GatewayHandler.HandleGatewayMessage` routes `vaulttypes.MethodPublicKeyGet` requests directly to `handlePublicKeyGet` instead of through `GatewayVaultRequestProcessor.ProcessRequest`, and `handlePublicKeyGet` unconditionally dereferences `*req.Params` without a nil check, unlike every sibling handler (`processCreateSecretsRequest`, `processUpdateSecretsRequest`, `processDeleteSecretsRequest`, `processListSecretIdentifiersRequest`, and even `handleSecretsCreate`/`Update`/`Delete`/`List` which rely on the processor's nil guard). A JSON-RPC `vault_publicKeyGet` request that omits `params` will cause a nil pointer dereference panic in this handler.

## Finding Description
`HandleGatewayMessage` dispatches by method: `MethodSecretsCreate/Update/Delete/List` go through `h.requestProcessor.ProcessRequest`, whose per-method implementations in `core/capabilities/vault/gateway_vault_request_processor.go` all explicitly check `req.Params == nil` before unmarshaling (e.g. `processDeleteSecretsRequest`). [1](#0-0) 

`MethodPublicKeyGet` instead goes straight to `handlePublicKeyGet`, which dereferences `*req.Params` with no nil guard: [2](#0-1) 

This is confirmed inconsistent with the nil-checks present for the sibling secret methods: [3](#0-2) 

I traced the front-end (gateway-side) path in `core/services/gateway/handlers/vault/handler.go`, which the original reporter could not fully verify. `HandleJSONRPCUserMessage` special-cases `MethodPublicKeyGet` and, on a cache miss, forwards the *raw, unvalidated user request* (including whatever `Params` value the caller supplied, including `nil`) straight to every DON node via `fanOutToVaultNodes`/`h.don.SendToNode`, with **no nil-Params check performed anywhere in that branch**: [4](#0-3) [5](#0-4) 

The node-side connector read loop unmarshals whatever arrives from the gateway and dispatches it directly to the registered handler, with no visible panic-recovery wrapper around this dispatch: [6](#0-5) 

One caveat that limits full end-to-end certainty: the top-level gateway HTTP entrypoint `gateway.ProcessRequest` unconditionally calls `g.codec.DecodeJSONRequest(jsonRequest)` for every incoming request before any handler-specific logic runs, and that function itself dereferences `*request.Params` without a nil check: [7](#0-6) [8](#0-7) 
Whether this earlier dereference itself panics (or is short-circuited/normalized upstream by `jsonrpc2.DecodeRequest`, which lives in the external `chainlink-common` module and is outside this repo's index) could not be confirmed. If it does not panic there, the path through `handler.go` → `fanOutToVaultNodes` → node's `handlePublicKeyGet` is real and unguarded, as shown above.

## Impact Explanation
A confirmed nil pointer dereference exists in `handlePublicKeyGet` and is not defended against by any check in `HandleGatewayMessage`'s dispatch or in the gateway-side `handler.go`'s `MethodPublicKeyGet` special path — the general request-validation pipeline (`GatewayVaultRequestProcessor`) that protects the other four Vault methods is deliberately bypassed for this method. If the request reaches the node process, this is a Denial-of-Service against the node's Vault gateway-connector goroutine (crash), analogous to a null-pointer-dereference DoS.

## Likelihood Explanation
The gateway-side `handler.go` code that specifically handles `MethodPublicKeyGet` forwards the request without any params validation, which is a genuine, verifiable gap (this addresses the reporter's stated uncertainty about the front-end). Full end-to-end reachability from an anonymous HTTP client still depends on behavior of the external `jsonrpc2.DecodeRequest`/`DecodeJSONRequest` codec step that runs earlier in `gateway.ProcessRequest`, which could not be fully verified with the tools available in this session (that logic sits in the `chainlink-common` dependency, not in this repo). Regardless of that outer layer, the node-side handler itself has zero defense-in-depth against nil `Params`, which is inconsistent with every sibling handler in the same file and represents a real, reproducible defect within this repo that should be fixed independent of the outer-layer question.

## Recommendation
Add `if req.Params == nil { return h.errorResponse(ctx, gatewayID, req, api.InvalidParamsError, errors.New("request params must not be nil")) }` at the top of `handlePublicKeyGet` in `core/capabilities/vault/gw_handler.go`, matching the pattern already used in `gateway_vault_request_processor.go`. Additionally, add the same guard to the gateway-side `handler.go`'s `MethodPublicKeyGet` branch, and verify (or add) a nil-check in `jsonrpccodec.go`'s `DecodeJSONRequest` for defense-in-depth at the outermost entrypoint.

## Proof of Concept
Unit test target: call `GatewayHandler.handlePublicKeyGet` (or `HandleGatewayMessage`) directly with a `*jsonrpc.Request[json.RawMessage]{Method: vaulttypes.MethodPublicKeyGet, Params: nil}` — this reproduces the panic entirely within this repo's code without needing the external `jsonrpc2` codec, at `core/capabilities/vault/gw_handler.go:366` (`json.Unmarshal(*req.Params, r)`). For an integration-level PoC, submit `{"jsonrpc":"2.0","id":"1","method":"vault_publicKeyGet"}` (no `params` field) to the gateway's public HTTP endpoint and observe whether it triggers a panic in `handler.go`'s `fetchVaultPublicKey`/`HandleJSONRPCUserMessage` path before or after forwarding to nodes.

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

**File:** core/services/gateway/handlers/vault/handler.go (L736-752)
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

	if len(nodeErrors) == len(h.donConfig.Members) && len(nodeErrors) > 0 {
		return h.sendResponse(ctx, ar, h.errorResponse(ar.req, api.FatalError, errors.New("failed to forward user request to nodes"), nil))
	}

	l.Debugw("successfully forwarded request to Vault nodes")
	return nil
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

**File:** core/services/gateway/api/jsonrpccodec.go (L26-35)
```go
func (*JSONRPCCodec) DecodeJSONRequest(request jsonrpc2.Request[json.RawMessage]) (*Message, error) {
	var msg Message
	err := json.Unmarshal(*request.Params, &msg)
	if err != nil {
		return nil, err
	}
	msg.Body.MessageID = request.ID
	msg.Body.Method = request.Method
	return &msg, nil
}
```

**File:** core/services/gateway/gateway.go (L221-230)
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
```
