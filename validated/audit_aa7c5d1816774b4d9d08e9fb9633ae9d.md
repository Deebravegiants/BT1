Based on my review of the actual source file, the claim is accurate to the code as it exists.

Audit Report

## Title
Missing allowlist/rate-limiting on Gateway `HandleLegacyUserMessage` allows unbounded fan-out of unprivileged user requests to all DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

## Summary
`HandleLegacyUserMessage` accepts `web_api_trigger` messages from external users, performs only payload decoding and a staleness check, and then unconditionally stores the request in the shared `savedCallbacks` map and fans it out to every DON member via `don.SendToNode`, with no allowlist or rate-limit check applied — the code explicitly leaves this as a `// TODO: apply allowlist and rate-limiting here`. [1](#0-0)  This lets an unprivileged sender who can produce validly-signed, non-stale messages flood `savedCallbacks` and multiply load onto all DON nodes at negligible cost.

## Finding Description
The handler decodes the payload and checks for a zero/stale timestamp [2](#0-1) , then hits the TODO before validating the method, with no sender allowlist or per-sender/global rate limiter applied at any point in this path [1](#0-0) . Immediately after, it unconditionally stores a `savedCallback` keyed by `msg.Body.MessageID` and loops over `h.donConfig.Members`, calling `don.SendToNode` for each one: [3](#0-2) . The only protection on `savedCallbacks` growth is the periodic `pruneCallbacks` job, gated by `CallbackMaxAgeSec`/`MaxSavedCallbacks` (defaults 120s / 20000 entries, trimming to half on overflow) [4](#0-3) [5](#0-4) . The `nodeRateLimiter` field that exists on the handler is only invoked in `handleWebAPIOutgoingMessage`, which throttles gateway→node HTTP delivery of target/action/syncer responses, not the ingress path from users through `HandleLegacyUserMessage` [6](#0-5) . The handler's own test suite documents this as an open gap rather than a validated/tested control.

## Impact Explanation
This maps to a denial-of-service against the Gateway's user-facing `web_api_trigger` capability: an unprivileged actor can exhaust the shared, bounded `savedCallbacks` cache (causing legitimate in-flight callbacks to be evicted/lost) and force amplified fan-out load onto every DON member node with each request, degrading availability of the capability across the whole DON. This is a real, code-confirmed gap rather than a speculative one, though it is a resource-exhaustion/availability issue rather than a direct authentication bypass, fund movement, or secret exfiltration — it should be scoped as Medium-severity DoS, consistent with the report's own assessment.

## Likelihood Explanation
Reachability requires only that an unprivileged external client can produce a message that passes the JSON payload decode and non-stale-timestamp checks and reaches `HandleLegacyUserMessage`; there is no allowlist or authentication gate specific to sender identity implemented in this function before the callback is saved and fanned out. The literal TODO comment and the corresponding untested/unimplemented assertion in `handler_test.go` corroborate that no such check exists in this code path today.

## Recommendation
Implement the allowlist and rate-limiting check at the `// TODO` marker in `HandleLegacyUserMessage`: validate `msg.Body.Sender` against a configured allowlist for the DON/trigger, and apply a per-sender and/or global rate limiter (reusing `ratelimit.RateLimiter`, mirroring `nodeRateLimiter`, or the `allowedSenders`/`rateLimiter` pattern used in `core/capabilities/webapi/trigger/trigger.go`) before storing the callback in `savedCallbacks` and fanning the request out to `h.donConfig.Members`.

## Proof of Concept
No dynamic reproduction was performed (static analysis only). A concrete test plan: instantiate a `handler` via `NewHandler` with a small `MaxSavedCallbacks`/`CallbackPruneIntervalSec`, then repeatedly invoke `HandleLegacyUserMessage` with distinct `MessageID`s and valid signatures from the same/different unauthenticated sender, asserting (a) `savedCallbacks` grows without any rejection prior to the prune cycle, and (b) `don.SendToNode` (mocked) is invoked once per DON member per request, demonstrating unbounded per-request fan-out multiplication with no sender-based gating.

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

**File:** core/services/gateway/handlers/capabilities/handler.go (L359-383)
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
