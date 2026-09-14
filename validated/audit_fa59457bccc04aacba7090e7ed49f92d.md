### Title
Unbounded Growth of RequestReplayGuard's `seen` Map Enables Memory-Exhaustion DoS via Vault Request Replay Protection - (File: core/capabilities/vault/request_replay_guard.go)

### Summary
`RequestReplayGuard`, used by both the AllowListBasedAuth and JWTBasedAuth flows to prevent replay of already-authorized Vault requests, stores every seen request digest in an in-memory map with no upper bound on the number of entries. [1](#0-0)  The map is only cleaned lazily, either as a side effect of a subsequent `CheckAndRecord` call or via an explicit `ClearExpired` call, and there is no limit on the total number of distinct digests that can be recorded before expiry. [2](#0-1) 

### Finding Description
Each call to `CheckAndRecord(digest, expiresAtUnix)` inserts the digest into `g.seen` if it is not already present and not expired, and only prunes entries that are already past their expiry timestamp at call time. [3](#0-2)  Because the digest is derived from the request contents/JWT digest, an unprivileged or unauthenticated caller who can reach the authorization path (`AuthorizeRequest`) can generate arbitrarily many unique request digests (e.g., by varying request IDs, params, or nonces) before their JWT/authorization expiry, causing `g.seen` to grow without any hard cap. Since pruning is opportunistic and keyed on expiry (which can be set far in the future depending on the caller-controlled token), this permits sustained, unbounded memory growth from repeated client requests — this is the direct analog of the reported "no array length limit" issue, translated to a Go map that grows without a size ceiling under attacker control.

### Impact Explanation
This can lead to gateway/node memory exhaustion under sustained request volume with distinct digests, since `g.seen` accumulates one entry per unique digest until expiry, with no enforced maximum table size to bound memory in a hostile/high-throughput scenario. Given this guard sits on the authorization path for Vault-related gateway requests, exhausting the node's memory would deny availability of the Vault authorization flow.

### Likelihood Explanation
Moderate. Exploitation requires an unprivileged client to be able to trigger many distinct authorization attempts (each with a fresh digest) within the token's validity window, which is generally not rate-limited within `RequestReplayGuard` itself. However, this is bounded by upstream rate limiters (if any) on the calling handlers, and by the requirement that requests still need to reach `AuthorizeRequest`, which may itself require some level of valid token structure. I could not fully verify (due to running out of tool iterations) whether call sites of `CheckAndRecord`/`AuthorizeRequest` in `core/capabilities/vault/authorizer.go` are protected by an upstream global/per-caller rate limiter that would meaningfully cap growth; this uncertainty affects the practical likelihood.

### Recommendation
Add an explicit maximum size to `RequestReplayGuard.seen` (analogous to `maxSavedCallbacks`/`maxCacheSize` patterns used elsewhere in the gateway, e.g. `defaultMaxSavedCallbacks` in the capabilities handler [4](#0-3)  and `maxCacheSize` in `requestCache` [5](#0-4) ). When the cap is reached, either reject new entries with a clear error, evict the oldest/soonest-to-expire entries, or apply a periodic background `ClearExpired()` sweep decoupled from request-triggered pruning so that unbounded caller-controlled growth cannot occur between prunes.

### Proof of Concept
1. An unprivileged client obtains (or is issued) a token allowing repeated calls to the Vault authorization path guarded by `RequestReplayGuard.CheckAndRecord`.
2. The client issues many distinct requests, each producing a unique digest (e.g., varying `request_id`/params), all with expiry timestamps far in the future.
3. Each call inserts a new entry into `g.seen` via `CheckAndRecord`; because `clearExpiredLocked()` only removes entries whose expiry has already passed, none of these entries are removed. [3](#0-2) 
4. Repeating this at scale grows `g.seen` unbounded, increasing memory usage on the node running the authorizer, degrading or eventually crashing the process — the functional equivalent of the reported unbounded-array growth issue.

### Citations

**File:** core/capabilities/vault/request_replay_guard.go (L11-28)
```go
// RequestReplayGuard prevents replay of already-processed requests by tracking
// request digests with expiry timestamps. It is safe for concurrent use.
//
// Used by both the AllowListBasedAuth flow and the JWTBasedAuth flow to ensure
// that a given request digest is only accepted once.
type RequestReplayGuard struct {
	mu      sync.Mutex
	seen    map[string]int64 // digest → unix expiry timestamp
	nowFunc func() time.Time // injectable for testing
}

// NewRequestReplayGuard creates a replay guard for authorized Vault requests.
func NewRequestReplayGuard() *RequestReplayGuard {
	return &RequestReplayGuard{
		seen:    make(map[string]int64),
		nowFunc: time.Now,
	}
}
```

**File:** core/capabilities/vault/request_replay_guard.go (L35-64)
```go
func (g *RequestReplayGuard) CheckAndRecord(digest string, expiresAtUnix int64) error {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.clearExpiredLocked()

	if _, exists := g.seen[digest]; exists {
		return ErrRequestAlreadySeen
	}

	g.seen[digest] = expiresAtUnix
	return nil
}

// ClearExpired removes all entries whose expiry timestamp is in the past.
// Call this to eagerly reclaim memory even when CheckAndRecord is not invoked.
func (g *RequestReplayGuard) ClearExpired() {
	g.mu.Lock()
	defer g.mu.Unlock()
	g.clearExpiredLocked()
}

func (g *RequestReplayGuard) clearExpiredLocked() {
	now := g.nowFunc().UTC().Unix()
	for digest, expiry := range g.seen {
		if now > expiry {
			delete(g.seen, digest)
		}
	}
}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L43-45)
```go
	defaultCallbackMaxAgeSec        = 120   // 2 minutes
	defaultMaxSavedCallbacks        = 20000 // could briefly exceed under heavy load
	defaultCallbackPruneIntervalSec = 30
```

**File:** core/services/gateway/handlers/common/requestcache.go (L27-31)
```go
type requestCache[T any] struct {
	cache        map[globalID]*pendingRequest[T]
	maxCacheSize uint32
	timeout      time.Duration
	mu           sync.Mutex
```
