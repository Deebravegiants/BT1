Based on the investigation, I found a genuine analog but need to be precise about what is proven vs. what is uncertain.

### Title
Unbounded per-sender rate-limiter map growth allows memory-exhaustion DoS from unauthenticated/unprivileged senders - ([File: core/services/workflows/ratelimiter/ratelimiter.go])

### Summary
The Xen CVE describes oxenstored failing to enforce `quota-maxentity` because of unspecified evaluation order, letting an unprivileged guest write unbounded entries and exhaust host memory. The closest reachable analog in this codebase is the `RateLimiter.Allow` implementation used to rate-limit unprivileged/external senders on gateway-facing paths: it lazily creates and permanently retains a `perSender` map entry for every distinct sender string it sees, with no cap on distinct senders and no eviction, so the "quota" mechanism itself becomes an unbounded-memory vector when driven by attacker-controlled sender identifiers.

### Finding Description
`RateLimiter.Allow` in [1](#0-0)  takes a `sender` string and, if it is not already present in `rl.perSender`, creates a brand-new `*rate.Limiter` and inserts it into the map — permanently, for the lifetime of the process:

```go
func (rl *RateLimiter) Allow(sender string) (senderAllow bool, globalAllow bool) {
	rl.mu.Lock()
	senderLimiter, ok := rl.perSender[sender]
	if !ok {
		senderLimiter = rate.NewLimiter(rate.Limit(rl.config.PerSenderRPS), rl.config.PerSenderBurst)
		rl.perSender[sender] = senderLimiter
	}
	rl.mu.Unlock()
	...
``` [2](#0-1) 

There is no maximum on the number of distinct `sender` keys, no TTL/eviction of stale senders, and no bound on `perSender` map size. The `PerSenderRPS`/`PerSenderBurst` values only bound the rate *per identity*; they do nothing to bound the *number of identities* the limiter will track, which is precisely analogous to `quota-maxentity` in the CVE being bypassable so that an actor can create unbounded "entries" instead of unbounded xenstore writes.

This limiter type is instantiated for workflow/dispatcher-facing rate limiting: `NewRateLimiter` is used to build `s.WorkflowRateLimiter` in `core/services/cre/cre.go` (`ratelimiter.NewRateLimiter(ratelimiter.Config{...})`) [3](#0-2) , and the same "one-key-per-first-use, no bound" pattern shows up in the confirmed-similar limiter in `core/capabilities/remote/dispatcher.go`, which calls `d.rateLimiter.Allow(sender)` where `sender := msg.Sender.String()` for every inbound P2P message before any authentication/authorization check narrows the sender set [4](#0-3) .

I was **not able to fully confirm**, within the tool budget available, the exact call site that feeds an *unauthenticated, fully attacker-controlled, high-cardinality* string (e.g., an arbitrary JSON-RPC field an unprivileged HTTP/gateway caller can set on every request) directly into `ratelimiter.RateLimiter.Allow` for the `workflows/ratelimiter` package specifically (as opposed to the `chainlink-common/pkg/ratelimit` package used by `OutgoingConnectorHandler` and `triggerConnectorHandler`, whose implementation I did not get to inspect in this session). The `dispatcher.go` sender comes from a P2P-DON peer ID (a semi-privileged, DON-registered signer), which weakens the "unprivileged actor" argument for that specific call site — sender identity there is bounded by DON membership, not by arbitrary external input.

### Impact Explanation
If a caller can supply an attacker-controlled, high-cardinality string as `sender` (e.g., a workflow ID, execution ID, or other free-form identifier from an unauthenticated/lightly-authenticated request) on a hot path guarded by this limiter, each unique value permanently allocates a new `rate.Limiter` in the `perSender` map. Because entries are never evicted, an attacker can drive unbounded heap growth purely by varying the sender field across requests — a memory-exhaustion DoS analogous to the Xen quota bypass, though bounded here by whatever surrounding request-rate/global limiter exists (which throttles rate but not map cardinality).

### Likelihood Explanation
Medium-Low, contingent on unresolved call-site verification. The `perSender` growth is unconditional and requires no privilege to trigger once a caller can reach `Allow()` with a controllable sender string, but I could not confirm within this session whether the specific `core/services/workflows/ratelimiter` package (as opposed to `chainlink-common/pkg/ratelimit`, used by the two gateway-message handlers with clearer unprivileged reach) is on such an unauthenticated path. This needs to be verified against the actual call graph of `s.WorkflowRateLimiter` before treating it as confirmed.

### Recommendation
- Add an upper bound on `perSender` map size (e.g., LRU eviction or TTL-based expiry) in `RateLimiter`, mirroring the eviction patterns already used elsewhere in the codebase (e.g., `ModuleLRU.enforceCapLocked` in `core/services/workflows/syncer/v2/evictable_module.go`, or `RequestReplayGuard.clearExpiredLocked` in `core/capabilities/vault/request_replay_guard.go`).
- Audit every caller of `ratelimiter.NewRateLimiter`/`RateLimiter.Allow` (and the sibling `chainlink-common/pkg/ratelimit.RateLimiter`) to confirm whether the `sender` value is attacker-controlled before authentication; if so, cap cardinality or key the limiter on a post-authentication, bounded-cardinality identity instead of a raw request field.

### Proof of Concept
Not independently verified end-to-end (no confirmed unauthenticated call site was located in this session). Conceptually: repeatedly call the vulnerable path with a freshly generated, unique `sender` string per request (e.g., random workflow/execution IDs) to observe unbounded growth of the `perSender` map and corresponding heap growth, with no corresponding cap or eviction ever triggered.

### Citations

**File:** core/services/workflows/ratelimiter/ratelimiter.go (L10-16)
```go
// Wrapper around Go's rate.Limiter that supports both global and a per-sender rate limiting.
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

**File:** core/services/cre/cre.go (L184-192)
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
```

**File:** core/capabilities/remote/dispatcher.go (L285-293)
```go
func (d *dispatcher) handleMessage(ctx context.Context, msg *p2ptypes.Message) {
	sender := msg.Sender.String()
	if !d.rateLimiter.Allow(sender) {
		d.metrics.rateLimitedMsgsCounter.Add(ctx, 1, metric.WithAttributes(
			attribute.String("sender", sender),
		))
		d.lggr.Errorw("rate limit exceeded, dropping message", "sender", msg.Sender)
		return
	}
```
