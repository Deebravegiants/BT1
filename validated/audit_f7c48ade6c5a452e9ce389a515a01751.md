### Title
Legacy WebAPI gateway handler forwards unauthenticated `web_api_trigger` messages to workflow nodes without any allowlist/authorization check - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The legacy Web API capability gateway handler's `HandleLegacyUserMessage` accepts inbound user messages and forwards them to all DON members for the `web_api_trigger` method with only a method-name and staleness check — no allowlist, authentication, or per-owner authorization is applied, despite an explicit TODO acknowledging this gap.

### Finding Description
`HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` validates only that the payload can be unmarshalled, that `Timestamp` is non-zero, that the message isn't stale, and that `msg.Body.Method == MethodWebAPITrigger`. Immediately after those checks there is an explicit comment `// TODO: apply allowlist and rate-limiting here`, and the code proceeds to save the callback and broadcast the raw request to every DON member via `don.SendToNode`. [1](#0-0) 

This stands in clear contrast to:
- The newer HTTP capability handler (`v2/http_handler.go`), which explicitly refuses legacy messages (`HandleLegacyUserMessage` returns an error) and instead routes JSON-RPC user requests through `triggerHandler.HandleUserTriggerRequest`, which performs org/allowlist-based authorization before dispatch. [2](#0-1) 
- The Vault capability's gateway handler, which routes every mutating/listing method through `GatewayVaultRequestProcessor.ProcessRequest`, which in turn calls an `Authorizer` (allowlist- or JWT-based) before any secret operation is performed. [3](#0-2) [4](#0-3) 

In the legacy handler, an unprivileged/unauthenticated external caller reaching the gateway's user-facing entrypoint can cause a `web_api_trigger` request to be relayed to every node in the DON (`for _, member := range h.donConfig.Members { ... don.SendToNode(ctx, member.Address, req) }`), triggering workflow execution on the node side without the gateway itself verifying that the caller/owner is permitted to invoke that workflow. [5](#0-4) 

### Impact Explanation
If this legacy handler path is still wired into a running gateway configuration (it implements the same `handlers.Handler` interface used by `multihandler.go`/`handler_factory.go`), any external, unauthenticated caller able to reach the gateway's user message endpoint could cause arbitrary `web_api_trigger` requests to be broadcast to workflow DON nodes, potentially triggering unauthorized workflow/job runs. This matches the report's bug class of "unprivileged actor able to invoke a privileged action due to a missing authorization check," analogous to calling `mintRebalancer`/`burnRebalancer` without `onlyBalancer`.

### Likelihood Explanation
Likelihood depends entirely on whether this legacy code path is still enabled/reachable in a deployed gateway configuration versus being superseded by the v2 HTTP capability handler. The code explicitly still exists, is exported, implements the `Handler` interface, and is referenced in `handler_factory.go` and `multihandler.go`, but I could not fully confirm from the available index whether it is instantiated in current production gateway configs or is dead/legacy-only code retained for backward compatibility. This uncertainty should be resolved before treating this as a confirmed exploitable finding — a Devin session with full repo/config access would be needed to trace `handler_factory.go`'s handler construction logic and any feature flags gating the legacy vs. v2 path.

### Recommendation
- Confirm whether `capabilities.NewHandler` (legacy) is still instantiated by `handler_factory.go` for any active DON/gateway configuration.
- If reachable, add allowlist/authorization enforcement in `HandleLegacyUserMessage` before broadcasting to DON members, mirroring the vault handler's `Authorizer`/`AllowListBasedAuth` pattern or the v2 handler's trigger-authorization flow.
- If the legacy path is intentionally deprecated and unreachable in practice, consider removing it or making `HandleLegacyUserMessage` unconditionally return an error (as `v2/http_handler.go` already does) to eliminate the exposure entirely.

### Proof of Concept
Not independently reproducible from the indexed code alone (no test harness confirming the legacy handler is wired into a live gateway route was found). Conceptually: an external client sends a JSON message with `Method: "web_api_trigger"` and a valid non-stale `Timestamp` to the gateway's legacy message endpoint; `HandleLegacyUserMessage` accepts it without any allowlist check and forwards it to every DON member, per the code cited above.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L388-402)
```go
func (h *gatewayHandler) HandleLegacyUserMessage(context.Context, *api.Message, handlers.Callback) error {
	return errors.New("HTTP capability gateway handler does not support legacy messages")
}

func (h *gatewayHandler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback handlers.Callback) error {
	h.metrics.IncrementTriggerRequestCount(ctx, h.lggr)
	err := h.triggerHandler.HandleUserTriggerRequest(ctx, &req, callback, time.Now())
	if err != nil {
		h.lggr.Errorw("failed to handle user trigger request", "requestID",
			req.ID, "err", err)
		// error response is sent to the response channel by the trigger handler
		// so return nil after logging
	}
	return nil
}
```

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

**File:** core/capabilities/vault/allow_list_based_auth.go (L32-62)
```go
// AuthorizeRequest authorizes a request using AllowListBasedAuth.
// It does NOT check if the request method is allowed.
func (r *allowListBasedAuth) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	r.lggr.Debugw("AllowListBasedAuth authorizing request", "method", req.Method, "requestID", req.ID)
	requestDigest, err := req.Digest()
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to create digest", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, err
	}
	requestDigestBytes, err := hex.DecodeString(requestDigest)
	if err != nil {
		r.lggr.Debugw("AllowListBasedAuth failed to decode digest", "method", req.Method, "requestID", req.ID, "requestDigest", requestDigest, "error", err)
		return nil, err
	}
	requestDigestBytes32 := [32]byte(requestDigestBytes)
	if r.workflowRegistrySyncer == nil {
		r.lggr.Errorw("AllowListBasedAuth workflowRegistrySyncer is nil", "method", req.Method, "requestID", req.ID)
		return nil, errors.New("internal error: workflowRegistrySyncer is nil")
	}
	allowlistedRequest, allowedRequestsStrs, err := r.findAllowlistedItemWithRetry(ctx, req, requestDigest, requestDigestBytes32)
	if err != nil {
		return nil, err
	}
	if allowlistedRequest == nil {
		r.lggr.Debugw("AllowListBasedAuth request digest not allowlisted",
			"method", req.Method,
			"requestID", req.ID,
			"digestHexStr", requestDigest,
			"allowedRequestsStrs", allowedRequestsStrs)
		return nil, errors.New("request not allowlisted")
	}
```
