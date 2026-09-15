Audit Report

## Title
Unauthenticated flood of `web_api_trigger` requests exhausts the shared `savedCallbacks` bound, causing cross-user response loss/DoS in the Gateway's legacy capability handler - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`handler.HandleLegacyUserMessage` accepts legacy `web_api_trigger` requests from the Gateway's internet-facing user HTTP endpoint and inserts every request into a single, DON-wide, size-bounded map `savedCallbacks` (capped at `MaxSavedCallbacks`, default 20000) with no per-sender rate limiting, as explicitly flagged by an inline `// TODO: apply allowlist and rate-limiting here`. Any actor capable of generating a self-chosen ECDSA keypair (no permission or allowlisting required) can sign and submit enough unique, fresh `web_api_trigger` messages to force `pruneCallbacks` to evict the oldest half of the map, silently dropping other users' in-flight callbacks and causing their requests to time out.

## Finding Description
`gateway.ProcessRequest` routes any DON-ID-addressed legacy JSON-RPC request straight into `h.HandleLegacyUserMessage(ctx, msg, callback)` [1](#0-0) , reachable from the internet-facing `httpServer` registered via `SetHTTPRequestHandler` [2](#0-1) .

`Message.Validate()` requires a structurally valid, recoverable ECDSA signature and derives `m.Body.Sender` from it via `ExtractSigner` [3](#0-2) , but this only proves the caller controls *some* private key — it performs no allowlist check against permitted senders. Anyone can generate an arbitrary keypair locally and sign messages with it, so this check does not gate who may submit legacy trigger requests.

Inside `HandleLegacyUserMessage`, right after basic payload/timestamp validation, the code explicitly acknowledges missing controls before accepting the method:
```go
// TODO: apply allowlist and rate-limiting here
if msg.Body.Method != MethodWebAPITrigger {
``` [4](#0-3) 

It then unconditionally inserts the callback into the shared map and fans the request out to all DON members:
```go
h.mu.Lock()
h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
don := h.don
h.mu.Unlock()

for _, member := range h.donConfig.Members {
    err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
}
``` [5](#0-4) 

`savedCallbacks` is bounded only by a global `MaxSavedCallbacks` (default 20000) and pruned by evicting the oldest half whenever the map exceeds that size, with no per-sender partitioning:
```go
maxSize := h.config.MaxSavedCallbacks
...
if len(h.savedCallbacks) > maxSize {
    ...
    for _, e := range entries[:len(entries)-maxSize/2] {
        delete(h.savedCallbacks, e.id)
        evicted++
    }
}
``` [6](#0-5) 

The only rate limiter present in this handler, `nodeRateLimiter`, is applied solely in `handleWebAPIOutgoingMessage` for outbound requests *from* DON nodes [7](#0-6)  — it is never consulted in `HandleLegacyUserMessage`, confirming there is no rate limiting on the inbound user path. This contrasts with the v2 HTTP trigger handler, which enforces `userRateLimiter.AllowErr` per workflow/owner before accepting a request [8](#0-7) .

When a real node response for an evicted `MessageID` eventually arrives, `handleWebAPITriggerMessage` finds `found == false` and silently drops it without notifying the sender:
```go
savedCb, found := h.savedCallbacks[msg.Body.MessageID]
delete(h.savedCallbacks, msg.Body.MessageID)
...
if found {
    return savedCb.SendResponse(...)
}
return nil
``` [9](#0-8) 

The evicted legitimate caller's original blocked `callback.Wait(ctx)` in `gateway.ProcessRequest` eventually times out and returns `RequestTimeoutError` [10](#0-9) .

## Impact Explanation
This is an availability/DoS issue: a single unprivileged actor, needing only a self-generated signing key (no allowlisting, credential, or role), can flood the Gateway's legacy `web_api_trigger` path to evict other tenants' pending callbacks from the shared, DON-wide `savedCallbacks` map, causing their legitimate in-flight requests to silently fail or time out. This degrades the gateway's function/availability for all legitimate users sharing a DON, matching the "cross-user response corruption"/availability impact class called out in the validation rules.

## Likelihood Explanation
Likelihood is high on any deployment still exposing this legacy handler: the attack requires only crafting well-formed, self-signed JSON-RPC legacy `web_api_trigger` messages with unique `MessageID`s and fresh timestamps — trivial for any external client with network access to the Gateway's user port, since signature validation only proves possession of an arbitrary key, not membership in an allowlist. No rate limiter or allowlist exists on this specific ingestion path to throttle such a flood, as explicitly noted by the code's own `TODO`.

## Recommendation
Implement the pending `TODO` in `HandleLegacyUserMessage`: apply an allowlist (only accept requests from known/permitted senders) and per-sender/per-IP rate limiting mirroring the `userRateLimiter`/`checkRateLimit` pattern already used in the v2 HTTP trigger handler, before inserting entries into `savedCallbacks`. Additionally, partition `savedCallbacks` capacity per sender (or reject new entries once near capacity rather than evicting indiscriminately) so a single caller cannot evict other callers' pending callbacks.

## Proof of Concept
1. Identify a Gateway deployment exposing a DON via the legacy `web_api_trigger` method (`DonID` routed through `g.handlers[donID]` in `gateway.go`).
2. Generate an arbitrary ECDSA keypair locally (no permission needed) and use it to sign JSON-RPC legacy request bodies with unique `MessageID`s and `Timestamp`s within `MaxAllowedMessageAgeSec`.
3. Submit more than `MaxSavedCallbacks/2` (default 10,000) such requests to the Gateway's user HTTP port faster than the `CallbackPruneIntervalSec` (default 30s) prune cycle; each is accepted unconditionally by `HandleLegacyUserMessage` and inserted into `h.savedCallbacks`.
4. Concurrently, have a legitimate client submit a normal `web_api_trigger` request just before the flood.
5. Observe `pruneCallbacks` evict the oldest half of `savedCallbacks`, including the legitimate client's entry; when the DON node's real response for that `MessageID` arrives, `handleWebAPITriggerMessage` finds `found == false` and drops it, and the legitimate client's `callback.Wait(ctx)` in `gateway.ProcessRequest` times out with `RequestTimeoutError`, confirming cross-user denial-of-service.

### Citations

**File:** core/services/gateway/gateway.go (L170-183)
```go
func NewGateway(codec api.Codec, httpServer gw_net.HTTPServer, handlers map[string]handlers.Handler, serviceNameToDonID map[string]string, serviceToMultiHandler map[string]handlers.Handler, connMgr ConnectionManager, gMetrics *monitoring.GatewayMetrics, lggr logger.Logger) Gateway {
	gw := &gateway{
		codec:                 codec,
		httpServer:            httpServer,
		handlers:              handlers,
		serviceNameToDonID:    serviceNameToDonID,
		serviceToMultiHandler: serviceToMultiHandler,
		connMgr:               connMgr,
		gMetrics:              gMetrics,
		lggr:                  logger.Named(lggr, "Gateway"),
	}
	httpServer.SetHTTPRequestHandler(gw)
	return gw
}
```

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

**File:** core/services/gateway/gateway.go (L277-288)
```go
	if err != nil {
		return newError(jsonRequest.ID, api.HandlerError, err.Error())
	}

	response, err := callback.Wait(ctx)
	duration := time.Since(startTime)
	if err != nil {
		response := api.RequestTimeoutError
		g.gMetrics.RecordUserMsgHandlerDuration(ctx, method, response.String(), duration)
		g.gMetrics.RecordUserMsgHandlerInvocation(ctx, method, response.String())
		return newError(jsonRequest.ID, response, "handler timeout: "+err.Error())
	}
```

**File:** core/services/gateway/api/message.go (L54-88)
```go
func (m *Message) Validate() error {
	if m == nil {
		return errors.New("nil message")
	}
	if len(m.Signature) != MessageSignatureHexEncodedLen {
		return errors.New("invalid hex-encoded signature length")
	}
	if len(m.Body.MessageID) == 0 || len(m.Body.MessageID) > MessageIDMaxLen {
		return errors.New("invalid message ID length")
	}
	if strings.HasSuffix(m.Body.MessageID, NullChar) {
		return errors.New("message ID ending with null bytes")
	}
	if len(m.Body.Method) == 0 || len(m.Body.Method) > MessageMethodMaxLen {
		return errors.New("invalid method name length")
	}
	if strings.HasSuffix(m.Body.Method, NullChar) {
		return errors.New("method name ending with null bytes")
	}
	if len(m.Body.DonID) == 0 || len(m.Body.DonID) > MessageDonIDMaxLen {
		return errors.New("invalid DON ID length")
	}
	if strings.HasSuffix(m.Body.DonID, NullChar) {
		return errors.New("DON ID ending with null bytes")
	}
	if len(m.Body.Receiver) != 0 && len(m.Body.Receiver) != MessageReceiverLen {
		return errors.New("invalid Receiver length")
	}
	signerBytes, err := m.ExtractSigner()
	if err != nil {
		return err
	}
	m.Body.Sender = utils.StringToHex(string(signerBytes))
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L148-162)
```go
func (h *handler) handleWebAPITriggerMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.mu.Lock()
	savedCb, found := h.savedCallbacks[msg.Body.MessageID]
	delete(h.savedCallbacks, msg.Body.MessageID)
	h.mu.Unlock()

	if found {
		// Send first response from a node back to the user, ignore any other ones.
		// TODO: in practice, we should wait for at least 2F+1 nodes to respond and then return an aggregated response
		// back to the user.
		codec := api.JSONRPCCodec{}
		return savedCb.SendResponse(handlers.UserCallbackPayload{RawResponse: codec.EncodeLegacyResponse(msg), ErrorCode: api.NoError})
	}
	return nil
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-169)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
	var payload Request
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L314-334)
```go
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-396)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-420)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L392-417)
```go
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
