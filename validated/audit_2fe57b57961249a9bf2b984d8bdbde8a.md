### Title
Unbounded per-sender rate limiter map growth via WebAPI Trigger events allows memory-based DoS - (File: `core/services/workflows/ratelimiter/ratelimiter.go`)

### Summary
The `RateLimiter.Allow` method in `core/services/workflows/ratelimiter/ratelimiter.go` lazily creates and stores a new `rate.Limiter` entry in the `perSender` map for every distinct sender string it observes, with no cap on the number of distinct senders and no eviction mechanism, mirroring the reported bug class where an entity is added to a tracked collection without any check against a maximum size limit.

### Finding Description
`RateLimiter.Allow(sender string)` looks up `sender` in `rl.perSender`; if absent, it unconditionally inserts a brand-new `*rate.Limiter` keyed by that string: [1](#0-0) 

There is no `TOKEN_ADDRESS_LIMIT`-style bound on `len(rl.perSender)`, and nothing ever removes stale entries — directly analogous to `TokenWhitelist.addToken` never checking `TOKEN_ADDRESS_LIMIT` before appending to the whitelist.

This limiter is instantiated and driven by the WebAPI Trigger capability, where `sender` is taken from incoming trigger/event data supplied by external callers of the gateway-connected trigger, not from a fixed, bounded configuration set: [2](#0-1) 

Because `Allow` is invoked on the hot path for every incoming request/event and keys the map by an attacker-influenced sender identifier, an unprivileged caller who varies the sender value across many requests can force the map to grow without bound, since no capacity check exists anywhere in `ratelimiter.go`.

### Impact Explanation
Each new distinct sender value permanently allocates a `*rate.Limiter` in an in-memory map that is never pruned. An external, unprivileged caller who can influence the `sender` field of trigger requests routed through the WebAPI Trigger capability can therefore cause unbounded heap growth on the node, leading to increased memory pressure and potential out-of-memory conditions / degraded node performance — the same "out-of-gas"/"unbounded resource growth" class of impact called out in the source report, translated to an off-chain resource-exhaustion equivalent.

### Likelihood Explanation
Likelihood depends on whether the `sender` value passed into `Allow` is fully attacker-controlled (e.g., derived from request payload) versus constrained to the pre-registered `AllowedSenders` list validated at `RegisterTrigger` time. If callers are restricted to addresses within the trigger's configured `AllowedSenders` set, the practical impact is bounded by that list's size and this would not be independently exploitable. I was not able to fully trace the exact call site that invokes `RateLimiter.Allow` with per-request sender data (only the constructor call in `RegisterTrigger` was found within available context), so I cannot confirm with certainty that the `sender` argument passed to `Allow` at runtime is unauthenticated/unbounded input rather than a value already checked against `allowedSenders`. This should be verified against the runtime event-processing code path (e.g., wherever `webapiTrigger.rateLimiter.Allow(...)` is actually called per incoming event) before treating this as a confirmed, exploitable-by-unprivileged-actor finding.

### Recommendation
- Add an explicit cap on `len(rl.perSender)` in `Allow`, rejecting/evicting entries once a configurable maximum distinct-sender count is reached (mirroring the recommended `require(tokenCount < TOKEN_ADDRESS_LIMIT)` fix in the source report).
- Alternatively, evict idle per-sender limiters using an LRU or TTL-based cache instead of an unbounded `map[string]*rate.Limiter`.
- Confirm and, if necessary, enforce that `Allow` is only ever called with sender values already validated against the trigger's registered `allowedSenders` set, so the effective key space is bounded by that pre-validated configuration.

### Proof of Concept
Not independently verified end-to-end due to inability to trace the exact runtime call site feeding `sender` into `Allow`; the following demonstrates the unbounded-growth defect in isolation:
1. Construct a `ratelimiter.RateLimiter` via `NewRateLimiter`.
2. Repeatedly call `rl.Allow(sender)` with N distinct, unique `sender` strings.
3. Observe that `rl.perSender` grows to size N with no upper bound and no eviction, as shown by the unconditional insert in `core/services/workflows/ratelimiter/ratelimiter.go` lines 40-52 — confirming the missing "limit" check analogous to the reported `TokenWhitelist.addToken` defect.

### Citations

**File:** core/services/workflows/ratelimiter/ratelimiter.go (L40-52)
```go
func (rl *RateLimiter) Allow(sender string) (senderAllow bool, globalAllow bool) {
	rl.mu.Lock()
	senderLimiter, ok := rl.perSender[sender]
	if !ok {
		senderLimiter = rate.NewLimiter(rate.Limit(rl.config.PerSenderRPS), rl.config.PerSenderBurst)
		rl.perSender[sender] = senderLimiter
	}
	rl.mu.Unlock()

	senderAllow = senderLimiter.Allow()
	globalAllow = rl.global.Allow()
	return senderAllow, globalAllow
}
```

**File:** core/capabilities/webapi/trigger/trigger.go (L234-246)
```go
	rateLimiterConfig := reqConfig.RateLimiter
	commonRateLimiter := ratelimit.RateLimiterConfig{
		GlobalRPS:      rateLimiterConfig.GlobalRPS,
		GlobalBurst:    int(rateLimiterConfig.GlobalBurst),
		PerSenderRPS:   rateLimiterConfig.PerSenderRPS,
		PerSenderBurst: int(rateLimiterConfig.PerSenderBurst),
	}

	rateLimiter, err := ratelimit.NewRateLimiter(commonRateLimiter)
	if err != nil {
		return nil, err
	}

```
