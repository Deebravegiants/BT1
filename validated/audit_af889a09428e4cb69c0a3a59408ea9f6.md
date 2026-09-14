## Analysis

The external report describes an unrestricted, unfinished `add()` function that lets any caller push unbounded data into storage with no allowlist/rate-limit check. The strongest analog reachable from an unprivileged/unauthenticated client in this codebase is `HandleLegacyUserMessage` in the gateway capabilities handler.

### Title
Unauthenticated gateway user messages accepted into `savedCallbacks` map without allowlist or rate-limiting - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
`(*handler).HandleLegacyUserMessage` accepts an inbound `api.Message` from an external gateway client, validates only payload shape/timestamp/method, and then unconditionally inserts an entry into `h.savedCallbacks` keyed by `msg.Body.MessageID`, fanning the message out to every DON member — with a `TODO: apply allowlist and rate-limiting here` left directly in the code path. [1](#0-0) [2](#0-1) 

### Finding Description
The handler performs stale-message and method checks, but the comment `// TODO: apply allowlist and rate-limiting here` confirms that the intended access-restriction logic (allowlisting which senders/workflows may submit web-API trigger messages, and rate-limiting how often they may do so) was never implemented for this legacy code path. [3](#0-2) 
Any caller able to reach this handler can therefore keep inserting into `h.savedCallbacks` and cause the message to be broadcast to every DON member node via `don.SendToNode`, without being checked against a workflow/sender allowlist or throttled per sender — mirroring the reported `add()` bug class (unrestricted push into an internal store/queue). [2](#0-1) 

Mitigating factor: `pruneCallbacks` does cap the total map size (`MaxSavedCallbacks`) and expire old entries, so the map itself cannot grow unbounded in memory. However, the *lack of per-sender allowlist/rate-limit* on this ingestion path is the concrete unfinished-logic gap that matches the bug class, since it still allows an unauthenticated actor to trigger unlimited DON-wide fan-out messages up to the eviction threshold, potentially crowding out legitimate callbacks and causing repeated broadcasts to all DON nodes. [4](#0-3) 

### Impact Explanation
An unauthenticated/unprivileged client sending crafted `api.Message`s can flood `savedCallbacks` and force fan-out sends to every member of the DON on each message, with no verification that the sender/workflow is authorized to trigger the DON. This can degrade gateway and DON node availability (resource/bandwidth exhaustion, callback slot eviction of legitimate in-flight requests) — an availability-impact issue consistent with the original "spam the storage / make contract unusable" report, though contained by the eviction-based cap rather than fully unbounded growth.

### Likelihood Explanation
Likelihood is moderate: the code path is reachable by any external message reaching this legacy handler (the comment explicitly states allowlist/rate-limiting is not yet applied), so exploitation only requires the ability to send a validly-shaped `api.Message` with a fresh timestamp and the `MethodWebAPITrigger` method — no signature/identity verification of the sender is shown in this snippet.

### Recommendation
Implement the intended allowlist and rate-limiting logic before accepting/fanning out `HandleLegacyUserMessage` requests, as the TODO indicates, rather than leaving it unfinished; alternatively, if this legacy path is deprecated in favor of the JSON-RPC path (`HandleJSONRPCUserMessage`, which explicitly returns an error for this handler), remove `HandleLegacyUserMessage` entirely to eliminate the unrestricted entry point. [5](#0-4) 

### Proof of Concept
Not independently verified with a live environment. Based on static review: an external actor sends an `api.Message` with `Body.Method = MethodWebAPITrigger`, a valid non-zero `Timestamp` within `MaxAllowedMessageAgeSec`, and any `MessageID`, to the gateway's legacy inbound path; `HandleLegacyUserMessage` will register a callback and broadcast the request to every DON member without any allowlist or per-sender rate-limit check, since that logic is marked as a pending TODO in the source. [6](#0-5) 

**Caveat / uncertainty:** I could not confirm from the index (a) whether an outer transport layer (e.g., an HTTP gateway server or connection-manager layer) applies its own authentication/allowlist before messages reach `HandleLegacyUserMessage`, or (b) whether this legacy path is still wired up in production configs versus being superseded by the JSON-RPC-based `httpTriggerHandler` path (which does have JWT auth and rate limiting, as seen in `http_trigger_handler.go`). Given index size limits, some surrounding wiring/config files may not be fully indexed — if you need certainty on whether this path is actually exposed and unauthenticated in the current deployment, a full Devin session with repo access would be needed to trace the call sites into `HandleLegacyUserMessage` and any outer auth middleware.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L295-297)
```go
func (h *handler) HandleJSONRPCUserMessage(_ context.Context, _ jsonrpc.Request[json.RawMessage], _ handlers.Callback) error {
	return errors.New("capabilities handler does not support JSON-RPC user messages")
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-420)
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
