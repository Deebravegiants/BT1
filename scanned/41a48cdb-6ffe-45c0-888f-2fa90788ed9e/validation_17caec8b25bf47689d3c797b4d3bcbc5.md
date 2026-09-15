### Title
Missing allowlist and rate-limiting on gateway legacy `web_api_trigger` user messages allows unauthenticated fan-out DoS - (File: `core/services/gateway/handlers/capabilities/handler.go`)

### Summary
The gateway's legacy WebAPI capability handler explicitly defers allowlist and rate-limit enforcement on inbound user trigger messages, marked by a `// TODO: apply allowlist and rate-limiting here` comment. Any unprivileged client reaching this handler's `HandleLegacyUserMessage` entry point can force the gateway to fan out a request to every DON member and register a tracked callback, with no per-sender or global throttling anywhere in the code path before that fan-out occurs.

### Finding Description
`handler.HandleLegacyUserMessage` (`core/services/gateway/handlers/capabilities/handler.go:341-421`) processes user-submitted `web_api_trigger` messages arriving at the gateway's internet-facing handler. The only gating performed before the request is dispatched to the workflow DON is:
- JSON payload unmarshal [1](#0-0) 
- a non-zero timestamp check [2](#0-1) 
- a "staleness" check computed from `payload.Timestamp`, a value fully controlled by the caller [3](#0-2) 
- a method-name check [4](#0-3) 

None of these validate the sender's identity, authorization, or request rate. The code then unconditionally stores a `savedCallback` entry keyed by the caller-supplied `MessageID` and sends the request to **every** DON member: [5](#0-4) .

This contrasts with the newer v2 HTTP trigger path, which enforces JWT authentication, workflow-owner rate limiting, and workflow-scoped authorization before any DON dispatch [6](#0-5) , and the outgoing connector handler, which applies per-sender and global rate limiting on gateway responses [7](#0-6) . The legacy handler lacks the equivalent protection entirely, and the responsible engineers left it as an open TODO rather than a completed control.

The `savedCallbacks` map does have a size-bounded pruning routine (`pruneCallbacks`, capped at `MaxSavedCallbacks`, default 20000, pruned every `CallbackPruneIntervalSec`) [8](#0-7) , which limits unbounded memory growth from this specific map, but it does nothing to prevent the CPU/network cost of repeatedly fanning a flood of invalid or high-volume requests out to all DON members, nor the DON-side cost each member incurs processing them.

### Impact Explanation
This directly mirrors the referenced CVE's bug class ("specially crafted... unconfirmed transactions/messages could cause unnecessary resource usage" before proper validation/authorization). Here, an unprivileged internet client can repeatedly submit `web_api_trigger` legacy messages to the gateway; each one is unconditionally broadcast to every node in the DON with no allowlist, JWT, or rate-limit check gating that fan-out. This allows amplification: one request from an attacker becomes N requests (one per DON member), consuming node CPU/network resources and callback bookkeeping, causing a denial-of-service condition on the gateway and the DON nodes it serves.

### Likelihood Explanation
Likelihood is high assuming this legacy handler is still wired up and reachable from the public-facing gateway HTTP endpoint (the same `handlers.Handler` interface used by the actively-tested v2 HTTP handler). The code is unauthenticated by design at this stage of the pipeline — no credentials, signatures, or per-sender identity are required to pass the checks that exist. I was not able to fully confirm from the indexed code whether this legacy code path is still registered/reachable in current production gateway configurations versus having been fully superseded by the v2 HTTP handler; this should be verified in the routing/config wiring (`core/services/gateway/handlers`, DON config `Services`) before treating this as exploitable in a specific deployment.

### Recommendation
- Implement the allowlist and rate-limiting referenced by the TODO before any DON dispatch or `savedCallbacks` registration in `HandleLegacyUserMessage`.
- Apply per-sender/global rate limiting consistent with the pattern already used in `OutgoingConnectorHandler.HandleGatewayMessage` and the v2 `httpTriggerHandler.checkRateLimit`.
- If the legacy handler is deprecated/unused in production, confirm it is not registered in any active gateway configuration, or remove it entirely to eliminate the exposure.

### Proof of Concept
1. An unauthenticated client sends repeated `web_api_trigger` `HandleLegacyUserMessage` requests to the gateway's public endpoint with valid-looking JSON payloads (non-zero `Timestamp`, correct `Method`).
2. Each request passes the only checks present (JSON parse, timestamp non-zero, staleness, method match) — none of which require identity or throttle rate.
3. Each request causes the gateway to call `don.SendToNode` once per DON member (`core/services/gateway/handlers/capabilities/handler.go:417-419`), multiplying attacker traffic by DON size and registering a `savedCallback` entry per request.
4. Repeating this at volume exhausts gateway and DON-node CPU/goroutine/network resources before any authorization or rate-limit rejection is possible, since none is implemented in this path.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L343-357)
```go
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-370)
```go
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L372-383)
```go
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

**File:** core/capabilities/webapi/outgoing_connector_handler.go (L318-349)
```go
	senderAllow, globalAllow := c.incomingRateLimiter.AllowVerbose(body.Sender)
	errJSON := jsonrpc.WireError{
		Code:    500,
		Message: "",
	}
	if !senderAllow {
		errJSON.Message = errorIncomingRatelimitSender
	}
	if !globalAllow {
		if errJSON.Message == "" {
			errJSON.Message = errorIncomingRatelimitGlobal
		} else {
			errJSON.Message += "\n" + errorIncomingRatelimitGlobal
		}
	}

	if errJSON.Message != "" {
		l.Errorw("request rate-limited")
		errPayload, err := json.Marshal(errJSON)
		if err != nil {
			l.Errorw("failed to marshal err payload", "err", err)
		}
		errMsg := api.Message{
			Body: api.MessageBody{
				MessageID: body.MessageID,
				Method:    api.MethodInternalError,
				Payload:   errPayload,
			},
		}
		ch <- &errMsg
		return nil
	}
```
