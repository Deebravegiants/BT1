### Title
Unauthenticated gateway user requests are not rate-limited or allowlisted before consuming shared callback capacity and being fanned out to the DON - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The gateway's legacy user-message entry point for the `web_api_trigger` capability method (`handler.HandleLegacyUserMessage`) forwards any externally-submitted trigger request to every node in the DON and registers a callback slot for it, with an explicit `// TODO: apply allowlist and rate-limiting here` marking that no allowlist or rate-limit check is actually performed before doing so. [1](#0-0) 

### Finding Description
`HandleLegacyUserMessage` validates only structural/timing properties of an incoming message (payload decodability, non-zero timestamp, message freshness, and that the method equals `MethodWebAPITrigger`), then unconditionally stores a `savedCallback` keyed by the caller-supplied `msg.Body.MessageID` and relays the request to every DON member: [2](#0-1) 

There is no per-sender authentication/allowlist check and no rate limiting applied at this call site — the code comment itself documents that this control is missing (`"TODO: apply allowlist and rate-limiting here"`), unlike the node-facing path (`handleWebAPIOutgoingMessage`), which does enforce `h.nodeRateLimiter.Allow(nodeAddr)`: [3](#0-2) 

The `savedCallbacks` map has a bounded capacity (`defaultMaxSavedCallbacks = 20000`), with periodic pruning that evicts the *oldest* entries once the cap is exceeded: [4](#0-3) [5](#0-4) 

This is directly analogous to the reservation bug: like `setreservationforlongterm`, which lets an unpriced, unauthenticated actor occupy a shared, bounded resource (rental-period slots) and block legitimate users, `HandleLegacyUserMessage` lets any unauthenticated caller occupy a shared, bounded resource (the `savedCallbacks` slot table and DON fan-out capacity) at zero cost and with no allowlist/quota gate, before any legitimate request is processed.

### Impact Explanation
An unauthenticated party can flood the gateway with `web_api_trigger` messages. Each message:
1. Consumes a slot in the shared, capacity-bounded `savedCallbacks` map, and
2. Is forwarded to all DON members, consuming DON node processing capacity, without any allowlist or per-sender rate limit gating it.

Because eviction removes the oldest entries once the map exceeds capacity, sustained spam can cause legitimate, still-pending user callbacks to be evicted before a real node response arrives, silently dropping the response the legitimate caller was waiting for (functionally the same "block real users" outcome as the reservation DoS: legitimate users lose their slot due to unpriced abuse). It also creates unnecessary DON-wide traffic for every spam message, which can degrade node processing of legitimate trigger workloads.

### Likelihood Explanation
This function is the entry point for external, presumably unprivileged, user messages destined for the `web_api_trigger` capability. The path is only gated by structural checks (payload shape, timestamp freshness) — the explicit `TODO` comment confirms allowlist/rate-limiting was never implemented for this path. This makes exploitation straightforward for any caller who can reach the gateway's legacy user-message ingestion path, requiring no valid credentials or fee, similar to the ease with which the original reservation exploit could be repeated across multiple addresses.

### Recommendation
Implement the allowlist and rate-limiting checks referenced by the TODO before accepting and forwarding a `web_api_trigger` message in `HandleLegacyUserMessage`: validate the caller's sender identity against a DON/method-specific allowlist and apply a per-sender rate limiter (mirroring the `nodeRateLimiter` pattern already used in `handleWebAPIOutgoingMessage`) prior to registering the `savedCallback` entry and fanning the request out to DON members.

### Proof of Concept
Not independently reproduced against a live gateway in this analysis; the vulnerability is demonstrated by direct code inspection: `HandleLegacyUserMessage` reaches `h.savedCallbacks[...] = ...` and `don.SendToNode(...)` for every structurally-valid `MethodWebAPITrigger` message regardless of sender, with the only allowlist/rate-limit enforcement point marked unimplemented by the inline `TODO`. [6](#0-5)

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
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
