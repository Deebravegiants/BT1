### Title
Legacy WebAPI gateway handler skips allowlist and rate-limiting enforced by its JSON-RPC sibling - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's `capabilities` handler package exposes two parallel entry points for user-submitted messages that get forwarded to DON nodes: the legacy `HandleLegacyUserMessage` and the newer `HandleJSONRPCUserMessage`-style methods used elsewhere (e.g. `v2.gatewayHandler.HandleJSONRPCUserMessage`, `vault.handler.HandleJSONRPCUserMessage`). Every other user-message handler in the gateway (vault, v2 HTTP capability, http trigger) enforces authorization and/or rate-limiting before forwarding a request to nodes. `HandleLegacyUserMessage`, however, contains an explicit TODO acknowledging that this enforcement is missing, and unconditionally forwards the request to every DON member.

### Finding Description
`handler.HandleLegacyUserMessage` in [1](#0-0)  validates payload shape, checks message staleness, and checks the method is `MethodWebAPITrigger`, but explicitly skips authorization/allowlisting and rate limiting: [2](#0-1) 

The code comment `// TODO: apply allowlist and rate-limiting here` on line 384 is a direct admission that this enforcement, present on the "sibling" methods, is absent here. After the (incomplete) checks, the function immediately fans the message out to every DON member: [3](#0-2) 

By contrast, the analogous per-node-forwarding gateway handlers elsewhere in the codebase all gate the equivalent operation behind authorization and/or rate-limit checks before dispatching to nodes:
- The v2 HTTP capability trigger handler calls `authorizeRequest` and `checkRateLimit` before sending to nodes: [4](#0-3) 
- The vault gateway handler runs every secrets method through `requestProcessor.ProcessRequest` (which calls the `Authorizer`) before touching `secretsService`: [5](#0-4) 
- The `handler.HandleNodeMessage` counterpart for node-originated `web_api_trigger` responses does track a `nodeRateLimiter`, but that limiter is only applied on the node-response path (`handleWebAPIOutgoingMessage`), not on `HandleLegacyUserMessage`'s outbound fan-out to nodes: [6](#0-5) 

This is a structurally identical bug class to the reported StableSwapFacet issue: several sibling functions performing conceptually the same "gated forward" operation, where one path is missing the guard(s) (`whenNotPaused` there; allowlist/rate-limit here) that the other paths consistently apply.

### Impact Explanation
Because `HandleLegacyUserMessage` performs no allowlist/authorization check, any unprivileged client able to reach the gateway's legacy user-message entry point can submit a `web_api_trigger` request that is broadcast to all DON node members without proving it is an authorized sender for the target workflow. Combined with the absence of rate-limiting on this specific path, an unprivileged caller can flood every member of the DON with trigger messages, and — because no ownership/authorization binding is verified — can potentially spoof trigger requests to workflows they do not control on nodes that still route through this legacy handler.

### Likelihood Explanation
The comment `// TODO: apply allowlist and rate-limiting here` on line 384 confirms this is not a defense-in-depth situation but a known, currently-unimplemented gap. Reachability depends on whether `HandleLegacyUserMessage` is still wired into an active, internet/user-facing gateway route (versus a fully deprecated code path) — this could not be conclusively confirmed from the indexed code alone (the caller wiring for `HandleLegacyUserMessage` vs. `HandleJSONRPCUserMessage` in `gateway.go`/`multihandler.go` was only partially visible in the retrieved context). If the legacy path is still dispatched for live traffic, likelihood is high given the explicit, acknowledged omission of both controls.

### Recommendation
Apply the same authorization/allowlist and rate-limiting enforcement to `HandleLegacyUserMessage` that is applied in the JSON-RPC/v2 sibling handlers before forwarding requests to DON nodes — i.e., resolve the TODO at core/services/gateway/handlers/capabilities/handler.go:384 by invoking an authorizer (analogous to `authorizeRequest`/`ProcessRequest` in the other handlers) and a rate limiter (analogous to `checkRateLimit`/`nodeRateLimiter`) prior to the `don.SendToNode` fan-out. If the legacy path is intentionally deprecated and unreachable from any live gateway route, it should be removed entirely rather than left as a live but unguarded code path.

### Proof of Concept
Not directly executable from static analysis alone; the code path itself is the proof:
1. `HandleLegacyUserMessage` decodes a `TriggerRequestPayload`, checks only timestamp freshness and method name.
2. It does not call any `Authorizer`/allowlist equivalent (unlike `vault.handler.HandleJSONRPCUserMessage` at core/services/gateway/handlers/vault/handler.go:422-434, or `httpTriggerHandler.authorizeRequest` at core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:368-376).
3. It does not call any rate limiter (unlike `httpTriggerHandler.checkRateLimit` at core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:392-417).
4. It proceeds straight to `don.SendToNode` for every DON member: [7](#0-6)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-421)
```go
func (h *handler) HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback handlers.Callback) error {
	body := msg.Body
	var payload webapicap.TriggerRequestPayload
	codec := api.JSONRPCCodec{}
	err := json.Unmarshal(body.Payload, &payload)
	if err != nil {
		h.lggr.Errorw(ErrDecodingPayload, "err", err)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload+" "+err.Error(),
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if payload.Timestamp == 0 {
		h.lggr.Errorw(ErrDecodingPayload)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrDecodingPayload,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	if uint(time.Now().Unix())-h.config.MaxAllowedMessageAgeSec > uint(payload.Timestamp) { //nolint:gosec // G115: comparing unix timestamps, both fit within uint
		h.lggr.Errorw("stale message")
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.HandlerError),
				"stale message",
				nil,
			),
			ErrorCode: api.HandlerError,
		})
	}
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
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/vault/handler.go (L394-434)
```go
func (h *handler) HandleJSONRPCUserMessage(ctx context.Context, req jsonrpc.Request[json.RawMessage], callback gwhandlers.Callback) error {
	if req.ID == "" {
		return errors.New("request ID cannot be empty")
	}
	if len(req.ID) > 200 {
		// Arbitrary limit to prevent abuse
		return errors.New("request ID is too long: " + strconv.Itoa(len(req.ID)) + ". max is 200 characters")
	}

	h.lggr.Debugw("handling vault request", "method", req.Method, "requestID", req.ID, "request", req)
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
