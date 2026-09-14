### Title
Unbounded per-sender rate limiter map enables memory-exhaustion DoS - (File: core/services/workflows/ratelimiter/ratelimiter.go)

### Summary
The `RateLimiter` used to gate workflow/gateway traffic keeps a `perSender map[string]*rate.Limiter` that is populated on every new, distinct sender key and is never pruned or bounded. This mirrors the reported Y2K `rolloverQueue` issue: an unprivileged actor who can supply arbitrarily many distinct sender/owner identifiers causes unbounded growth of an in-memory structure, this time a map of live `*rate.Limiter` objects rather than a Solidity array, leading to sustained memory growth / resource exhaustion rather than a revert-on-loop, but the same root cause (unbounded, attacker-driven collection growth with no eviction).

### Finding Description
`RateLimiter.Allow` lazily creates and stores a new `*rate.Limiter` for every unseen `sender` key, with no cap, TTL, or eviction policy: [1](#0-0) [2](#0-1) 

This is structurally identical to the `enlistInRollover` bug class: a caller-controlled key (there, `_receiver`; here, `sender`) drives permanent growth of a shared collection that is never trimmed. This `RateLimiter` type is instantiated as the workflow-level `WorkflowRateLimiter` in `core/services/cre/cre.go` and referenced again in `core/services/workflows/syncer/v2/handler.go`, i.e. it is wired into the workflow-registry/syncer path rather than being scoped strictly to peer-to-peer traffic: [3](#0-2) 

By contrast, the analogous callback map in the gateway capability handler (`core/services/gateway/handlers/capabilities/handler.go`) explicitly bounds and prunes itself by age and size: [4](#0-3) 
No equivalent pruning exists for `ratelimiter.RateLimiter.perSender`.

### Impact Explanation
If the `sender`/owner key fed into `WorkflowRateLimiter.Allow` can be freely chosen by many distinct external, unprivileged actors (e.g., distinct workflow owner addresses processed by the workflow syncer), each new key permanently allocates a `*rate.Limiter` entry that is never removed for the life of the process. Sustained diversity of senders causes continuous, unbounded memory growth in the node process, a resource-exhaustion DoS analogous to the `rolloverQueue` growth in the reported bug, though the failure mode here is gradual memory exhaustion rather than a single out-of-gas loop.

### Likelihood Explanation
Confirmed at the data-structure level (no cap/TTL exists in `ratelimiter.go`), but I was not able to fully trace, within the remaining investigation budget, the exact call site in `core/services/workflows/syncer/v2/handler.go` that supplies the `sender` argument to `WorkflowRateLimiter.Allow`, nor confirm whether that value is fully attacker-chosen (e.g., an arbitrary on-chain workflow-owner address anyone can register) versus constrained/deduplicated elsewhere. This limits confidence in end-to-end exploitability; the finding should be validated by inspecting `handler.go`'s call into `WorkflowRateLimiter.Allow` and the cost/permission model for creating new distinct "sender" identities.

### Recommendation
Add bounded eviction to `ratelimiter.RateLimiter` (e.g., LRU cap, idle-TTL sweep similar to `pruneCallbacks` in `handler.go`) so `perSender` cannot grow without bound regardless of how many distinct sender identifiers are observed, and audit all call sites (workflow syncer, CRE services) to confirm the sender key space is not fully attacker-controlled.

### Proof of Concept
Not independently reproducible within the current investigation because the exact caller supplying `sender` in `core/services/workflows/syncer/v2/handler.go` was not confirmed. Conceptually: repeatedly invoke the code path that calls `WorkflowRateLimiter.Allow(sender)` with a fresh, previously-unseen `sender` value each time (e.g., a new workflow-owner identifier); each call permanently adds one entry to `perSender` in `core/services/workflows/ratelimiter/ratelimiter.go` (lines 40-52), with no code path ever removing entries, causing monotonic memory growth over time.

### Citations

**File:** core/services/workflows/ratelimiter/ratelimiter.go (L11-16)
```go
type RateLimiter struct {
	global    *rate.Limiter
	perSender map[string]*rate.Limiter
	config    Config
	mu        sync.Mutex
}
```

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

**File:** core/services/cre/cre.go (L184-193)
```go
	workflowRateLimiter, err := ratelimiter.NewRateLimiter(ratelimiter.Config{
		GlobalRPS:      capCfg.RateLimit().GlobalRPS(),
		GlobalBurst:    capCfg.RateLimit().GlobalBurst(),
		PerSenderRPS:   capCfg.RateLimit().PerSenderRPS(),
		PerSenderBurst: capCfg.RateLimit().PerSenderBurst(),
	})
	if err != nil {
		return nil, fmt.Errorf("could not instantiate workflow rate limiter: %w", err)
	}
	s.WorkflowRateLimiter = workflowRateLimiter
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-334)
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
```
