### Title
`MaxSavedCallbacks` limit is not enforced at insertion, allowing unbounded growth of the gateway's `savedCallbacks` map from unauthenticated/unprivileged user requests - ([File: core/services/gateway/handlers/capabilities/handler.go])

### Summary
The `WebAPIHandler` in the gateway declares a `MaxSavedCallbacks` configuration limit intended to bound the size of the in-memory `savedCallbacks` map, but this limit is never checked when a new entry is added. It is only enforced retroactively by a periodic pruning goroutine that runs every `CallbackPruneIntervalSec` (default 30s). This mirrors the reported bug class exactly: a configured limit exists (analogous to `TOKEN_ADDRESS_LIMIT`) but the corresponding "add" function (analogous to `addToken`) does not check it before mutating the collection that is iterated/looped over.

### Finding Description
`HandleLegacyUserMessage` unconditionally stores a new `savedCallback` into `h.savedCallbacks` for every incoming user trigger message, with no check against `h.config.MaxSavedCallbacks`: [1](#0-0) 

The only place the limit is consulted is inside `pruneCallbacks`, which runs on a fixed timer (`CallbackPruneIntervalSec`, default 30s) and evicts oldest entries down to `maxSize/2` *after* the map has already grown past `maxSize`: [2](#0-1) 

The handler config and defaults confirm the intended limit and its "soft" nature is acknowledged in code comments ("could briefly exceed under heavy load"): [3](#0-2) 

Critically, the code path that inserts into this map (`HandleLegacyUserMessage`) also has an explicit TODO acknowledging that rate-limiting/allowlisting is not yet applied to this ingress point: [4](#0-3) 

This means a workflow/user request that reaches this handler can insert into `savedCallbacks` at an unbounded rate for up to the full prune interval, with no admission check comparable to the recommended `require(tokenCount <= TOKEN_ADDRESS_LIMIT, ...)` pattern from the analog report.

### Impact Explanation
Because insertion is not gated by `MaxSavedCallbacks`, an unprivileged caller able to reach `HandleLegacyUserMessage` (any user-originated trigger message routed to this gateway handler) can flood the map with entries faster than the periodic pruner can catch up, causing unbounded memory growth on the gateway node for up to `CallbackPruneIntervalSec`. Under sustained load this is a resource-exhaustion/DoS vector against the gateway process, degrading or crashing gateway service availability for all DON members and users routed through it — directly analogous to the "out-of-gas when looping over unbounded collection" impact described in the source report, translated to a memory/availability impact for this off-chain component.

### Likelihood Explanation
Likelihood is moderate-to-high in adversarial conditions: the insertion path is on the normal user-request flow (`HandleLegacyUserMessage`), requires no privileged access, and the code explicitly notes that allowlisting/rate-limiting is not yet implemented for this path. An attacker only needs to generate enough distinct trigger messages within a 30-second window to grow the map arbitrarily before the next prune cycle.

### Recommendation
Enforce `MaxSavedCallbacks` at insertion time in `HandleLegacyUserMessage` (reject or apply backpressure once the map is at capacity), rather than relying solely on the periodic `pruneCallbacks` sweep. Additionally, implement the rate-limiting/allowlisting noted in the existing TODO comment for this ingress path to reduce the attack surface further.

### Proof of Concept
1. An unprivileged client sends a burst of unique `HandleLegacyUserMessage` trigger requests (each with a distinct `msg.Body.MessageID`) to the gateway's `WebAPIHandler` faster than `CallbackPruneIntervalSec` (default 30s).
2. Each request unconditionally executes `h.savedCallbacks[msg.Body.MessageID] = &savedCallback{...}` (lines 411-414) with no check against `MaxSavedCallbacks` (default 20000).
3. Because pruning only runs once per `CallbackPruneIntervalSec`, the map can grow well beyond `MaxSavedCallbacks` during that window, consuming gateway memory proportional to the attacker's request rate, not the configured cap.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-70)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
)

type handler struct {
	services.StateMachine
	config          HandlerConfig
	don             handlers.DON
	donConfig       *config.DONConfig
	savedCallbacks  map[string]*savedCallback
	mu              sync.Mutex
	lggr            logger.Logger
	httpClient      network.HTTPClient
	nodeRateLimiter *ratelimit.RateLimiter
	wg              sync.WaitGroup
	stopCh          services.StopChan
	metrics         *metrics
}

type HandlerConfig struct {
	NodeRateLimiter         ratelimit.RateLimiterConfig `json:"nodeRateLimiter"`
	MaxAllowedMessageAgeSec uint                        `json:"maxAllowedMessageAgeSec"`

	CallbackMaxAgeSec        int `json:"callbackMaxAgeSec"`
	MaxSavedCallbacks        int `json:"maxSavedCallbacks"`
	CallbackPruneIntervalSec int `json:"callbackPruneIntervalSec"`
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

**File:** core/services/gateway/handlers/capabilities/handler.go (L411-414)
```go
	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()
```
