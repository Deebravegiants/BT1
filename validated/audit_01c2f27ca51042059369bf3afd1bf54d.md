### Title
Missing allowlist/rate-limiting on Gateway `HandleLegacyUserMessage` allows unbounded fan-out of unprivileged user requests to all DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The `HandleLegacyUserMessage` function in the Gateway's capabilities handler accepts requests from unauthenticated/unprivileged external clients (any user who can reach the gateway's user-facing endpoint) and forwards them to every member node of the DON, while explicitly deferring the allowlist and rate-limit checks with a `// TODO: apply allowlist and rate-limiting here` comment. [1](#0-0) 

### Finding Description
`HandleLegacyUserMessage` is the entry point for user-originated `web_api_trigger` messages arriving at the gateway. It performs payload decoding and a staleness/timestamp check, but the code that is supposed to validate the sender against an allowlist and apply rate limiting is left as an unimplemented TODO: [2](#0-1) 

After these checks, the handler unconditionally stores a `savedCallback` entry keyed by `msg.Body.MessageID` in the shared `savedCallbacks` map, and fans the request out to **every** member of `h.donConfig.Members`: [3](#0-2) 

The only protection against unbounded growth of `savedCallbacks` is the periodic `pruneCallbacks` job, which runs on a fixed interval (`CallbackPruneIntervalSec`, default 30s) and only evicts entries once the map exceeds `MaxSavedCallbacks` (default 20000), trimming down to half that size: [4](#0-3) [5](#0-4) 

This mirrors the Oku bug class precisely: there is no "cost" (fee, allowlist membership check, or per-sender rate limit) required to submit a request that consumes shared, limited pending-request capacity (`savedCallbacks`) and triggers work fanned out to every DON node. A single unprivileged sender can repeatedly submit fresh `web_api_trigger` messages (each with a unique `MessageID`) to:
1. Fill `savedCallbacks` up toward `MaxSavedCallbacks`, causing legitimate users' callbacks to be evicted early by `pruneCallbacks` (their responses would then be dropped/lost when nodes eventually respond, since `handleWebAPITriggerMessage` looks up the callback by ID and does nothing if it's missing).
2. Force the gateway to call `don.SendToNode` for every DON member on every single request, multiplying load onto all workflow nodes with no cost to the attacker beyond crafting a validly-signed message.

Unlike the sibling JSON-RPC path (`HandleJSONRPCUserMessage`) which is not implemented for this handler, and unlike the newer confidential-relay/gateway v2 handlers which have `nodeRateLimiter`/`perNodeRateLimiters` and global rate limiters wired in for node-to-gateway traffic, the user-to-gateway direction in this legacy handler has no equivalent throttle — the only rate limiter present (`nodeRateLimiter`) protects gateway→node outgoing HTTP traffic, not the initial ingress from users: [6](#0-5) 

The handler's own test suite acknowledges this gap explicitly: [7](#0-6) 

### Impact Explanation
This is a Medium-severity denial-of-service analog to the Oku finding: an unprivileged, unauthenticated (from the gateway's perspective, un-allowlisted) actor can flood the gateway's shared pending-callback cache and force fan-out load onto every node in the DON with no economic or authorization barrier. This can starve/evict legitimate users' pending callbacks and degrade or deny the `web_api_trigger` capability across the whole DON, similar to how Bob's cheap repeated order creation/cancellation DOSed the Oku order book by exhausting the shared `pendingOrderIds` capacity.

### Likelihood Explanation
Likelihood is high for reachability: `HandleLegacyUserMessage` is invoked directly on the path from a gateway's user-facing HTTP/WS server for the `web_api_trigger` method, with no allowlist gate before the callback is saved and forwarded — confirmed by the literal TODO comment in the code and by the corresponding unimplemented test coverage. No privileged access or on-chain cost is required; only a validly formed/signed message with a non-stale timestamp, which is trivial and cheap for an attacker to produce repeatedly with unique `MessageID`s.

### Recommendation
Implement the allowlist and rate-limiting check that is stubbed out at the `// TODO` in `HandleLegacyUserMessage` before storing the callback and fanning out to DON members: validate `msg.Body.Sender` against a configured allowlist for the trigger/DON, and apply a per-sender (and/or global) rate limiter (the pattern already used elsewhere in the codebase, e.g. `ratelimit.RateLimiter` used for `nodeRateLimiter`, or the trigger-side `allowedSenders`/`rateLimiter` machinery in `core/capabilities/webapi/trigger/trigger.go`) so that unbounded, costless request flooding cannot exhaust the shared `savedCallbacks` cache or multiply load across all DON nodes.

### Proof of Concept
Not applicable/available from static analysis alone — reproduction would require standing up a Gateway with a configured DON and multiple nodes and issuing repeated `web_api_trigger` user messages with distinct `MessageID`s to observe `savedCallbacks` growth and fan-out amplification; this could not be executed in this read-only analysis.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-338)
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
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-396)
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

**File:** core/services/gateway/handlers/capabilities/handler_test.go (L360-366)
```go
		handler.mu.Lock()
		require.Empty(t, handler.savedCallbacks, "error paths must not leave entries in savedCallbacks")
		handler.mu.Unlock()
	})

	// TODO: Validate Senders and rate limit check, pending question in trigger about where senders and rate limits are validated
}
```
