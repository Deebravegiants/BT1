## Analog Finding

The reported bug class — a security middleware (input validation / allowlisting) that is applied on some route/handler paths but is missing from other, functionally-equivalent paths of the same internet-facing service — has a concrete analog in the chainlink gateway's capabilities handler.

### Title
Legacy WebAPI trigger message path in gateway capabilities handler is missing allowlist/rate-limit checks applied elsewhere - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's capabilities `handler` exposes two paths for incoming user messages that reach the internet-facing gateway: `HandleJSONRPCUserMessage` (rejected outright for this handler) and `HandleLegacyUserMessage`, which processes legacy `web_api_trigger` messages and forwards them to every DON member node. Unlike the newer v2 HTTP trigger handler, which enforces per-workflow authorization (`authorizeRequest`) and rate limiting (`checkRateLimit`) before dispatching work, `HandleLegacyUserMessage` has no equivalent allowlist or rate-limit check — this is explicitly flagged by a `TODO` comment left in the code.

### Finding Description
`HandleLegacyUserMessage` validates payload structure, decoding, and message staleness, but then dispatches the request to all DON nodes without any sender allowlist or rate-limiting check: [1](#0-0) 

By contrast, the newer HTTP trigger handler used for the same class of user-triggered workflow execution enforces an authorization check per workflow and a per-workflow rate limiter before proceeding: [2](#0-1) 

This mirrors exactly the pattern in the external report: a security control (there, `inputValidatorMiddleware()`; here, allowlist/rate-limiting) is consistently applied to one code path but not to a sibling path serving equivalent functionality, in a component reachable directly from unprivileged external callers via the gateway's HTTP `ProcessRequest` entrypoint: [3](#0-2) 

### Impact Explanation
Any external caller able to construct a valid legacy gateway message (which only needs to pass structural/decoding/staleness checks) can cause the gateway to broadcast a `web_api_trigger` request to every member node of the target DON with no allowlist restriction on sender identity and no rate limiting, unlike the equivalent v2 path. This is an unauthorized-request-fanout / quota-bypass condition: it can be used to flood DON nodes with triggered workflow executions or resource-consuming requests, bypassing the throttling and authorization protections that the newer handler path applies for the same class of action.

### Likelihood Explanation
The legacy path is reachable by any unprivileged client that can send a request to the gateway's public HTTP endpoint and craft a valid `api.Message` with method `web_api_trigger` — no additional privilege is required, since the missing checks are exactly the allowlist/rate-limit gates that would otherwise restrict this. The `TODO: apply allowlist and rate-limiting here` comment in the shipped code confirms the gap is a known, currently-unaddressed omission rather than a hypothetical one.

### Recommendation
Apply the same allowlist and rate-limiting controls used by the v2 HTTP trigger handler (`authorizeRequest`/workflow-scoped rate limiter) to `HandleLegacyUserMessage` before it saves the callback and dispatches to DON members, rather than relying on a `TODO` marker. Alternatively, retire the legacy path once callers have migrated, or gate it behind the same node/global rate limiter already used for `handleWebAPIOutgoingMessage`.

### Proof of Concept
1. Craft a legacy gateway `api.Message` with `Body.Method = "web_api_trigger"`, a valid non-zero `Timestamp`, and a well-formed `webapicap.TriggerRequestPayload`.
2. Submit it to the gateway's public HTTP endpoint so it is routed through `gateway.ProcessRequest` → `handler.HandleLegacyUserMessage`.
3. Observe that the message passes decoding/staleness checks and is forwarded to all DON members via `don.SendToNode`, with no allowlist or rate-limit rejection — contrasted with the v2 path, where an equivalent unauthenticated/unauthorized or rate-exceeding request is rejected by `authorizeRequest`/`checkRateLimit`.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-417)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
}

// resolveOrgID resolves the organization ID for owner, or returns "" if it can't be resolved
func (h *httpTriggerHandler) resolveOrgID(ctx context.Context, owner string) string {
	if h.orgResolver == nil {
		h.lggr.Warnw("OrgResolver is nil, continuing without an orgID", "workflowOwner", owner)
		return ""
	}
	orgID, err := h.orgResolver.Get(ctx, owner)
	if err != nil {
		h.lggr.Warnw("Failed to resolve organization ID, continuing without it", "workflowOwner", owner, "err", err)
		return ""
	}
	return orgID
}

func (h *httpTriggerHandler) checkRateLimit(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	workflowRef, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflow reference not found", callback)
		return errors.New("workflow reference not found")
	}

	orgID := h.resolveOrgID(ctx, workflowRef.workflowOwner)
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: workflowRef.workflowOwner, Org: orgID, Workflow: workflowID})
	if err := h.userRateLimiter.AllowErr(ctx); err != nil {
		lggr := logger.With(h.lggr, platform.KeyWorkflowID, workflowID, platform.KeyWorkflowOwner, workflowRef.workflowOwner, "requestID", requestID, "err", err)
		if errLimited, ok := errors.AsType[limits.ErrorRateLimited](err); ok {
			switch errLimited.Scope {
			case settings.ScopeWorkflow:
				lggr.Errorf("failed to start execution: per workflow rate limit exceeded")
				h.metrics.IncrementWorkflowThrottled(ctx, h.lggr)
			default:
				lggr.Errorf("failed to start execution: unexpected rate limit for scope %s", errLimited.Scope)
			}
			h.handleUserError(ctx, requestID, jsonrpc.ErrLimitExceeded, "rate limit exceeded", callback)
			return err
		}
		return fmt.Errorf("failed to check rate limit: %w", err)
	}
	return nil
}
```

**File:** core/services/gateway/gateway.go (L220-276)
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
