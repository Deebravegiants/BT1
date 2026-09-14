Confirmed: `gateway.ProcessRequest` (`core/services/gateway/gateway.go:221-295`) is the internet-facing HTTP entry point that dispatches any unauthenticated legacy request directly to `h.HandleLegacyUserMessage(ctx, msg, callback)` with no allowlist/authorization gate at the dispatch layer itself. [1](#0-0) 

### Title
Resource-consuming preflight processing (payload decode, request forwarding, callback-map growth) occurs before allowlist/authorization in `WebAPIHandler.HandleLegacyUserMessage` - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The gateway's legacy WebAPI capability handler decodes the request payload, validates timestamps, registers a per-request callback, and fans the message out to every DON member node before any allowlist or per-sender rate-limiting check is applied. A comment in the code explicitly documents this gap.

### Finding Description
`WebAPIHandler.HandleLegacyUserMessage` is invoked directly from the internet-facing `gateway.ProcessRequest` for any legacy (DON-ID-addressed) JSON-RPC request, with only structural `msg.Validate()` performed beforehand — no sender allowlist or authorization check. [1](#0-0) 

Inside the handler, the request payload is unmarshaled, a timestamp freshness check is performed, and then — explicitly marked by a `TODO: apply allowlist and rate-limiting here` — the method-name check passes straight through to constructing a JSON-RPC request, taking the global handler mutex to register a `savedCallback` entry keyed by `msg.Body.MessageID` in an unbounded (until periodic pruning) `h.savedCallbacks` map, and finally broadcasting the request to `don.SendToNode` for every member of the DON: [2](#0-1) 

The only capacity control is a periodic best-effort prune job (`pruneCallbacks`) that runs every `CallbackPruneIntervalSec` and only trims once `MaxSavedCallbacks` (default 20000) is exceeded: [3](#0-2) 

This is directly analogous to the OpenClaw advisory's bug class: expensive per-request work (transcription/preflight) is performed for an unauthenticated/unauthorized caller before any allowlist rejection, allowing pre-auth resource consumption. Here, every unauthenticated caller's request causes: JSON unmarshaling, a mutex-protected map write, and a fan-out RPC call to every node in the DON — all prior to any allowlist enforcement, which the code comment confirms is not yet implemented on this path.

### Impact Explanation
An unauthenticated caller reaching the gateway's HTTP endpoint can repeatedly submit legacy `web_api_trigger`-shaped requests, causing the gateway to (a) grow the `savedCallbacks` map (bounded only by periodic pruning, default every 30s / 20000 entries — "could briefly exceed under heavy load" per the code comment) and (b) forward a full RPC message to every node of the target DON for each request, multiplying load across the entire DON with a single malicious client request. This matches the CVSS vector of the referenced advisory: no confidentiality/integrity impact, but availability impact via unauthenticated resource consumption (CWE-770 uncontrolled resource consumption).

### Likelihood Explanation
High for triggering: the code path requires only a well-formed legacy JSON-RPC envelope with a valid `DonID` and passes `msg.Validate()` — no allowlist, API key, or per-sender rate limiting is enforced before the expensive fan-out occurs, since `nodeRateLimiter` is only applied on the outbound HTTP path in `handleWebAPIOutgoingMessage`, not on inbound user requests in `HandleLegacyUserMessage`. [4](#0-3) 

### Recommendation
Implement the allowlist/rate-limiting check noted in the `TODO` comment before registering the callback and before fanning the message out to DON nodes, e.g., verify the sender/workflow is allowlisted and apply a per-sender rate limit at the top of `HandleLegacyUserMessage`, mirroring the pattern already used by `httpTriggerHandler.authorizeRequest`/`checkRateLimit` in the v2 HTTP trigger path. [5](#0-4) 

### Proof of Concept
1. Send repeated legacy JSON-RPC requests to the gateway's public HTTP endpoint with `Body.DonID` set to a valid, configured DON and `Body.Method` = `web_api_trigger`, each with a unique `MessageID` and a fresh `Timestamp`.
2. Observe that each request causes `HandleLegacyUserMessage` to unmarshal the payload, insert an entry into `h.savedCallbacks`, and call `don.SendToNode` once per DON member — all without any allowlist or authentication check, since none is enforced on this path.
3. Repeat at high volume to observe growth of `savedCallbacks` and proportional multiplication of outbound node RPCs per attacker request, consistent with the CWE-770/CWE-408 resource-consumption class described in GHSA-hhff-fj5f-qg48.

### Citations

**File:** core/services/gateway/gateway.go (L253-276)
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
	} else {
		method = jsonRequest.Method
		err = h.HandleJSONRPCUserMessage(ctx, jsonRequest, callback)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-339)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}

	// If there are still too many callbacks, sort them by creation time and remove the oldest ones.
	maxSize := h.config.MaxSavedCallbacks
	var evicted int
	if len(h.savedCallbacks) > maxSize {
		type entry struct {
			id        string
			createdAt time.Time
		}
		entries := make([]entry, 0, len(h.savedCallbacks))
		for id, cb := range h.savedCallbacks {
			entries = append(entries, entry{id, cb.createdAt})
		}
		sort.Slice(entries, func(i, j int) bool {
			return entries[i].createdAt.Before(entries[j].createdAt)
		})
		// Trim to maxSize/2 to avoid sorting the list too frequently.
		for _, e := range entries[:len(entries)-maxSize/2] {
			delete(h.savedCallbacks, e.id)
			evicted++
		}
	}

	if expired > 0 || evicted > 0 {
		h.lggr.Infow("Pruned savedCallbacks", "expired", expired, "evicted", evicted, "remaining", len(h.savedCallbacks))
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
