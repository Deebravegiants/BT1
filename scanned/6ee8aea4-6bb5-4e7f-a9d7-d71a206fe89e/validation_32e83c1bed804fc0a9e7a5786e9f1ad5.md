### Title
Unbounded `savedCallbacks` map growth in gateway legacy Web API handler enables memory-exhaustion DoS - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The `handler.HandleLegacyUserMessage` function in the gateway's Web API capabilities handler inserts an entry into the in-memory `savedCallbacks` map for every incoming user request, with no per-request cap, allowlist, or rate-limit check at insertion time. Eviction only happens asynchronously via a periodic `pruneCallbacks` ticker, mirroring the reported "no maximum amount for minting" DoS class: an unprivileged caller can keep adding entries faster than they are pruned, growing the map without bound between prune cycles.

### Finding Description
`HandleLegacyUserMessage` validates payload structure/timestamp but explicitly skips any allowlist or rate-limiting logic — the code even contains the comment `// TODO: apply allowlist and rate-limiting here` immediately before unconditionally storing the callback: [1](#0-0) 

The only bound on map size, `MaxSavedCallbacks` (default `defaultMaxSavedCallbacks = 20000`), is enforced lazily by the `pruneCallbacks` goroutine, which runs only once per `CallbackPruneIntervalSec` (default 30s): [2](#0-1) [3](#0-2) [4](#0-3) 

Because insertion into `h.savedCallbacks` at line 412 is unconditional and unthrottled, and the comment at line 384 confirms rate limiting/allowlisting was never implemented for this path, a caller who submits requests faster than the 30-second prune interval can drain can grow the map arbitrarily large between prunes — directly analogous to `Game.sol#mintNewBasket` having no cap on how many baskets a caller can mint per unit time.

### Impact Explanation
Uncontrolled growth of `savedCallbacks` consumes gateway node memory and CPU (map operations, later sort during pruning), degrading or crashing the gateway process that serves all DON web-API/HTTP capability traffic — a denial-of-service against the gateway's message-routing service, not merely a single user's resource.

### Likelihood Explanation
Likelihood is high in principle for the code path itself (no limiter guards the insertion), but this analysis could not fully confirm from the indexed code whether the outer HTTP/gateway ingress layer (that ultimately calls `HandleLegacyUserMessage`) applies its own authentication/allowlist/rate-limit before dispatch. If the outer gateway ingress enforces per-sender rate limiting upstream (as seen elsewhere, e.g. `DefaultPerSenderRPS`/`DefaultPerSenderBurst` in `core/capabilities/webapi/outgoing_connector_handler.go`), the practical exploitability is reduced. This uncertainty should be verified against the full gateway request-dispatch code before treating this as confirmed-exploitable in production.

### Recommendation
- Enforce the `MaxSavedCallbacks` limit synchronously at insertion time in `HandleLegacyUserMessage` (reject/evict-oldest immediately) rather than relying solely on the periodic `pruneCallbacks` sweep.
- Implement the allowlist/rate-limiting noted in the `// TODO` comment on this specific ingress path, consistent with the per-sender rate limiting already used in other gateway handlers.

### Proof of Concept
Not independently reproduced; based on static code analysis of the cited insertion path (`core/services/gateway/handlers/capabilities/handler.go:411-414`) and lazy-eviction design (`pruneCallbacks`, lines 299-339). A concrete PoC would require exercising the full gateway ingress (HTTP → `HandleLegacyUserMessage`) to confirm whether upstream layers add missing throttling; this was not fully verifiable from the available index.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L269-285)
```go
func (h *handler) Start(context.Context) error {
	return h.StartOnce(handlerName, func() error {
		h.wg.Go(func() {
			ticker := time.NewTicker(time.Duration(h.config.CallbackPruneIntervalSec) * time.Second)
			defer ticker.Stop()
			for {
				select {
				case <-ticker.C:
					h.pruneCallbacks()
				case <-h.stopCh:
					return
				}
			}
		})
		return nil
	})
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
