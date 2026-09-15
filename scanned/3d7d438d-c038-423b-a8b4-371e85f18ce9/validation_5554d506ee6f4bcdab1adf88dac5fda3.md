### Title
Missing allowlist/authorization check in legacy WebAPI capability trigger handler allows unauthenticated user to fan-out arbitrary trigger messages to all DON nodes - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
`handler.HandleLegacyUserMessage` in the WebAPI capabilities gateway handler forwards any well-formed `web_api_trigger` message from an external, unauthenticated caller to every member of the DON without any allowlist, authorization, or per-caller rate-limiting check — the code even contains an explicit `// TODO: apply allowlist and rate-limiting here` marker at the exact point where such a check should occur.

### Finding Description
The gateway's `ProcessRequest` routes any legacy-style request (one that carries a `DonID`) directly to the matching handler's `HandleLegacyUserMessage` without applying any authorization at the gateway layer itself: [1](#0-0) , and then dispatches: [2](#0-1) .

Inside `handler.HandleLegacyUserMessage`, the code validates payload shape, timestamp/staleness, and method name, but the only allowlisting/rate-limiting step is a stub — a TODO comment sits directly above the method check with no implementation, and the flow proceeds to broadcast the caller-supplied request to every DON member: [3](#0-2) 

Contrast this with the sibling handlers in the same package tree that were built to require authorization before contacting nodes:
- The vault handler requires `ProcessRequest`/authorization before creating an active request: [4](#0-3) 
- The v2 HTTP trigger handler enforces JWT authorization (`authorizeRequest`) and per-workflow-owner rate limiting (`checkRateLimit`) before ever sending to nodes: [5](#0-4)  and [6](#0-5) 

The legacy WebAPI capabilities handler has no analogous check: it only verifies the message isn't stale and uses `MethodWebAPITrigger`, then immediately fans the request out to `h.donConfig.Members` via `don.SendToNode`. This is the direct analog of the reported bug class — a destination/consumer of a forwarded message is contacted without first checking a whitelist/authorization gate that the surrounding system design otherwise expects.

### Impact Explanation
Any unauthenticated caller able to reach the gateway's legacy JSON-RPC endpoint with a `DonID` targeting a WebAPI-capability DON can force the gateway to broadcast arbitrary trigger payloads to every node in that DON, with no per-caller identity check, workflow ownership check, or workflow-level rate limit (only a per-node/global inbound `nodeRateLimiter` inside `handleWebAPIOutgoingMessage`, which is a separate, later stage guarding node-originated outgoing HTTP fetches, not the initial trigger fan-out). This enables unauthorized job/trigger execution requests to be injected into DON nodes and can be used to spam/DoS the DON, bypassing the authorization model the newer v2 handler enforces.

### Likelihood Explanation
Moderate-to-high: no special conditions or attacker mistake are required (unlike the on-chain analog, which needs the caller to submit a malformed `to_handler`). Any client that can reach the gateway HTTP endpoint and knows a valid `DonID` mapped to this legacy WebAPI handler can trigger the flow, since `ProcessRequest` treats any request carrying `DonID` as legacy and routes it straight to `HandleLegacyUserMessage`.

### Recommendation
Implement the allowlist/authorization/rate-limiting check flagged by the TODO in `HandleLegacyUserMessage` before dispatching to DON members — e.g., verify the caller/workflow is registered and authorized for this DON's WebAPI capability (mirroring `authorizeRequest`/`checkRateLimit` in the v2 `httpTriggerHandler`), and apply per-caller/per-workflow rate limiting prior to the `don.SendToNode` fan-out loop.

### Proof of Concept
1. Send a JSON-RPC request to the gateway with `Body.DonID` set to a DON ID served by the legacy `capabilities.handler` (WebAPI capability) and `Body.Method = MethodWebAPITrigger`, with a valid (non-stale) `Timestamp` in `TriggerRequestPayload`.
2. `gateway.ProcessRequest` treats this as a legacy request purely based on presence of `DonID` and calls `h.HandleLegacyUserMessage` with no additional authorization: [7](#0-6) 
3. `HandleLegacyUserMessage` passes the staleness/method checks (both trivially satisfiable by the caller) and, without any allowlist gate, iterates `h.donConfig.Members` sending the request to every node: [8](#0-7) 
4. Repeating this with distinct `MessageID`s lets an unauthenticated caller flood every DON node with trigger messages, since no per-caller/workflow authorization or rate limit exists at this stage.

### Citations

**File:** core/services/gateway/gateway.go (L253-272)
```go
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
```

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

**File:** core/services/gateway/handlers/vault/handler.go (L422-441)
```go
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
	authorizedOwner := authorized.AuthResult.AuthorizedOwner()

	h.lggr.Debugw("handling authorized vault request", "method", req.Method, "requestID", req.ID, "authorizedOwner", authorizedOwner)
	ar, activeRequestErr := h.newActiveRequest(req, callback)
	if activeRequestErr != nil {
		return activeRequestErr
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
