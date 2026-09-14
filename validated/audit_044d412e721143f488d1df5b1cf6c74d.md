### Title
Web API Trigger requests reach all DON nodes with no allowlist or rate-limiting enforcement - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's capabilities handler explicitly forwards every incoming `web_api_trigger` user message to all DON nodes without applying any allowlist or rate-limiting check, despite an explicit `TODO` in the code acknowledging this gap. This is a message-envelope/handler-side analog of the "message sent to any origin" bug class: an unprivileged, internet-facing caller can get its request broadcast to all nodes of a DON without being vetted against any per-user/per-workflow allowlist.

### Finding Description
`HandleLegacyUserMessage` in [1](#0-0)  decodes the payload, checks timestamp/staleness and method name, then immediately proceeds to fan the request out to every DON member: [2](#0-1) 

The comment `// TODO: apply allowlist and rate-limiting here` sits directly above the method check, confirming that no allowlist or per-sender rate limiting is applied before the message is dispatched with `don.SendToNode` to every member of `h.donConfig.Members`. Unlike other handlers in the same package (e.g. the vault gateway handler, which authorizes each request via `Authorizer.AuthorizeRequest` before it is stamped and routed — see [3](#0-2)  and [4](#0-3) ), the capabilities `web_api_trigger` legacy path has no equivalent authorization/allowlist gate. There is only a rate limiter applied to node→gateway traffic (`nodeRateLimiter`, used in `handleWebAPIOutgoingMessage`, see [5](#0-4) ) — nothing bounds the volume or identity of gateway-facing (unprivileged client → gateway) `web_api_trigger` requests before they are broadcast to the DON.

### Impact Explanation
Because the request is broadcast to every DON node without allowlist enforcement, any caller able to reach the gateway's legacy user-message endpoint can trigger `web_api_trigger` workflow executions on all DON members. This can be used to invoke workflows that the caller is not authorized to trigger, cause unnecessary/expensive downstream workflow executions across the whole DON, or be leveraged as an amplification vector, since one client request becomes N node-directed messages with no admission control at the handler layer.

### Likelihood Explanation
The vulnerable code path is the default/legacy code path used for the `web_api_trigger` method (`MethodWebAPITrigger`), which is one of the handler's advertised `Methods()` ( [6](#0-5) ), reachable directly from `HandleLegacyUserMessage`, the entry point documented in the `Handler` interface as being invoked "for each user request" ( [7](#0-6) ). No additional authorization step exists upstream of this handler in the code paths inspected. The `TODO` comment itself is an admission by the Onbloc/Chainlink team that this control is intentionally deferred/missing, which raises confidence this is a real, currently-unaddressed gap rather than a false positive.

### Recommendation
Apply an allowlist check (analogous to the vault handler's `Authorizer.AuthorizeRequest`/`allowListBasedAuth` pattern) and per-sender rate limiting to `HandleLegacyUserMessage` before the request is broadcast via `don.SendToNode`, so that only allowlisted senders/workflows can trigger DON-wide dispatch of `web_api_trigger` messages.

### Proof of Concept
1. Send a JSON payload satisfying `webapicap.TriggerRequestPayload` (non-zero `Timestamp`, recent enough to pass the staleness check) with `Method` set to `web_api_trigger` to the gateway's legacy user-message endpoint, without any prior registration/allowlisting for the sender.
2. Observe in `HandleLegacyUserMessage` that after payload unmarshal, timestamp check, and method-name check pass, the code proceeds directly to `don.SendToNode` for every member in `h.donConfig.Members` ( [8](#0-7) ) — no allowlist lookup or authorization call occurs anywhere in the function, unlike the vault handler's equivalent flow.

**Note on uncertainty:** I was not able to fully trace whether there is an additional allowlist/authentication check performed further upstream (e.g., at the HTTP transport layer in `core/services/gateway/gateway.go`, `network`, or connector-manager code) before `HandleLegacyUserMessage` is invoked — searches of `gateway.go` for allowlist/rate-limiter keywords returned no matches, but the full request-routing chain (`gateway.go`, `multihandler.go`, connector manager) was not read in full due to iteration limits. If such an upstream check exists and applies specifically to this method/handler, it would reduce or eliminate the severity of this finding.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L239-246)
```go
func (h *handler) Methods() []string {
	return []string{
		MethodWebAPITrigger,
		MethodWebAPITarget,
		MethodComputeAction,
		MethodWorkflowSyncer,
	}
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L341-420)
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
```

**File:** core/capabilities/vault/gateway_vault_request_processor.go (L260-292)
```go
func (p *GatewayVaultRequestProcessor) authorizeAndStamp(
	ctx context.Context,
	req *jsonrpc.Request[json.RawMessage],
	stamp func(prefixedRequestID string) error,
) (*AuthorizedGatewayVaultRequest, error) {
	incomingOwner := ""
	if idx := strings.Index(req.ID, vaulttypes.RequestIDSeparator); idx != -1 {
		incomingOwner = req.ID[:idx]
	}

	p.lggr.Debugw("authorizing gateway vault request", "method", req.Method, "requestID", req.ID)
	authResult, err := p.authorizer.AuthorizeRequest(ctx, *req)
	if err != nil {
		authErr := fmt.Errorf("request not authorized: %w", err)
		p.lggr.Errorw("gateway vault request authorization failed", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "", "incomingOwner", incomingOwner, "error", authErr)
		return nil, authErr
	}

	originalRequestID := req.ID
	authorizedOwner := authResult.AuthorizedOwner()
	prefixedRequestID := authorizedOwner + vaulttypes.RequestIDSeparator + originalRequestID
	req.ID = prefixedRequestID

	if err := stamp(prefixedRequestID); err != nil {
		p.lggr.Errorw("failed to stamp authorized request params", "method", req.Method, "requestID", req.ID, "error", err)
		return nil, fmt.Errorf("failed to stamp authorized request params: %w", err)
	}

	p.lggr.Debugw("authorized gateway vault request", "method", req.Method, "requestID", req.ID, "owner", authorizedOwner, "orgID", authResult.OrgID(), "workflowOwner", authResult.WorkflowOwner())
	return &AuthorizedGatewayVaultRequest{
		Req:        *req,
		AuthResult: authResult,
	}, nil
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

**File:** core/services/gateway/handlers/handler.go (L34-37)
```go
	// Each user request is processed by a separate goroutine, which:
	//   1. calls HandleUserMessage
	//   2. waits on callbackCh with a timeout
	HandleLegacyUserMessage(ctx context.Context, msg *api.Message, callback Callback) error
```
