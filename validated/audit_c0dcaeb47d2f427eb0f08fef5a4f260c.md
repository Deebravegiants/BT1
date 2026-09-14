### Title
Unbounded per-request map scan in `RequestReplayGuard.CheckAndRecord` allows unprivileged Vault clients to degrade node-wide request authorization - ([File: core/capabilities/vault/request_replay_guard.go])

### Summary
Every Vault request that reaches a node through the gateway is authorized via `authorizer.AuthorizeRequest`, which unconditionally calls `RequestReplayGuard.CheckAndRecord` under a single global mutex [1](#0-0) . `CheckAndRecord` calls `clearExpiredLocked`, which does a full `for digest, expiry := range g.seen` scan of the entire replay-guard map on *every single call*, while holding the lock [2](#0-1) . This is structurally the same bug class as the reported `HookManager.sol` issue: an unbounded/linear iteration over a growing collection performed on a hot, externally-triggerable path, causing linearly increasing cost per request and lock contention that serializes authorization for the entire node.

### Finding Description
`RequestReplayGuard` tracks authorized request digests with expiry timestamps to prevent replay [3](#0-2) . It is used by both `AllowListBasedAuth` and `JWTBasedAuth` flows, wired into the shared `authorizer` used for every incoming Vault gateway request (`req.Auth == ""` uses allow-list auth, otherwise JWT auth) [4](#0-3) .

On every call to `AuthorizeRequest`, after the underlying auth mechanism succeeds, the code calls `a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt())` [5](#0-4) . `CheckAndRecord` takes a single mutex (`g.mu`) and, before checking/inserting the digest, calls `g.clearExpiredLocked()`, which iterates over the *entire* `seen` map to find expired entries [6](#0-5) . There is no cap on the number of entries that can accumulate in `seen`, and the expiry of each entry is controlled by `ExpiresAt()`, which for the allow-list path comes from the on-chain `ExpiryTimestamp` set by workflow owners — not bounded to a short window [7](#0-6) .

Because the scan happens under `g.mu.Lock()` for every single authorization call (both success paths that insert new digests and the check against replay), as the number of distinct in-flight/valid authorized digests grows, the per-request cost of `CheckAndRecord` grows linearly, and because it's a single mutex, all concurrent Vault request authorizations on the node serialize behind this one lock. This mirrors the reported analog exactly: an `EnumerableSet`/map-like structure iterated in full on every state-changing/validating call, with no upper bound on set size, creating an increasingly expensive - and ultimately node-DoS-capable - operation as usage grows.

### Impact Explanation
Any unprivileged client capable of sending Vault requests through the gateway (e.g., issuing many distinct valid or even distinctly-digested requests with far-future expiries) can grow `seen` without bound, since insertion happens on every successful authorization and there is no size limit or independent reaping mechanism guaranteed to run frequently enough to offset growth under load. As the map grows, `clearExpiredLocked`'s full scan makes every subsequent Vault request authorization on the node progressively slower, and since it is done under a single mutex shared across all authorization flows (allow-list and JWT), this can serialize/delay all Vault operations for all workflow owners on that node — a node-wide availability degradation caused by an unprivileged actor's request volume, not by any node/peer misbehavior.

### Likelihood Explanation
Likelihood is moderate: the attacker need only be able to generate many distinct authorized (or otherwise digest-varying) Vault requests, which is within reach of any unprivileged workflow owner/client using the existing allow-list or JWT Vault flow — no privileged access or malicious node/peer behavior is required. The severity of the degradation depends on how large `seen` can practically grow before expiry-driven cleanup catches up, which was not fully confirmed within available context (e.g., whether `ClearExpired` is invoked periodically by a background job outside of `CheckAndRecord`); this is analogous to the referenced report's caveat that impact scales with set/collection size over time.

### Recommendation
Bound the cost of replay-guard maintenance so it is not proportional to accumulated map size on the hot authorization path:
- Amortize/rate-limit the expired-entry sweep (e.g., only run `clearExpiredLocked` periodically via a background ticker instead of on every `CheckAndRecord` call), decoupling cleanup cost from request throughput.
- Impose an explicit upper bound on the number of tracked digests (e.g., LRU eviction or a hard cap tied to configuration), rejecting or evicting oldest entries once the cap is reached.
- Consider sharding the replay-guard lock/map (e.g., by digest prefix) to reduce lock contention under concurrent load, similar to how the external report recommends bounding hook-set size instead of unconditionally iterating it in full on every hot-path call.

### Proof of Concept
Conceptual reproduction (not executed):
1. Obtain/derive N distinct valid authorizations (allow-list or JWT based) each with a distinct request digest and an expiry far in the future.
2. Submit these N Vault requests through the gateway in sequence/parallel so each calls `authorizer.AuthorizeRequest` → `replayGuard.CheckAndRecord` [5](#0-4) .
3. Each call inserts a new entry into `g.seen` and every subsequent call performs a full `O(len(seen))` scan under `g.mu` in `clearExpiredLocked` [6](#0-5) .
4. As N grows, wall-clock time per Vault request authorization increases roughly linearly, and because the lock is global, concurrent Vault traffic for all users on that node is serialized and slowed, demonstrating the DoS-class impact without requiring any privileged or malicious-node behavior.

### Citations

**File:** core/capabilities/vault/authorizer.go (L99-112)
```go
func (a *authorizer) AuthorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	authResult, err := a.authorizeRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	if authResult == nil {
		err = errors.New("auth mechanism returned nil auth result")
		a.lggr.Errorw("auth mechanism returned nil auth result", "method", req.Method, "requestID", req.ID, "hasAuth", req.Auth != "")
		return nil, err
	}
	if err := a.replayGuard.CheckAndRecord(authResult.Digest(), authResult.ExpiresAt()); err != nil {
		a.lggr.Debugw("replay guard rejected request", "method", req.Method, "requestID", req.ID, "owner", authResult.AuthorizedOwner(), "digest", authResult.Digest(), "expiresAt", authResult.ExpiresAt(), "hasAuth", req.Auth != "", "error", err)
		return nil, err
	}
```

**File:** core/capabilities/vault/authorizer.go (L121-128)
```go
func (a *authorizer) authorizeRequest(ctx context.Context, req jsonrpc.Request[json.RawMessage]) (*AuthResult, error) {
	// Requests without req.Auth continue using the allowlist-based path for backwards compatibility.
	// Existing clients do not populate the auth field yet, so treating an empty value as JWT would break them.
	if req.Auth == "" {
		return a.authorizeAllowListBasedAuth(ctx, req)
	}
	return a.authorizeJWTBasedAuth(ctx, req)
}
```

**File:** core/capabilities/vault/request_replay_guard.go (L11-20)
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
```

**File:** core/capabilities/vault/request_replay_guard.go (L35-63)
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
```

**File:** core/capabilities/vault/allow_list_based_auth.go (L64-76)
```go
	if time.Now().UTC().Unix() > int64(allowlistedRequest.ExpiryTimestamp) {
		authorizedRequestStr := string(allowlistedRequest.RequestDigest[:])
		r.lggr.Debugw("AllowListBasedAuth authorization expired", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", authorizedRequestStr, "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
		return nil, errors.New("request authorization expired")
	}

	digestKey := string(allowlistedRequest.RequestDigest[:])
	r.lggr.Debugw("AllowListBasedAuth authorization succeeded", "method", req.Method, "requestID", req.ID, "authorizedRequestStr", digestKey, "owner", allowlistedRequest.Owner.Hex(), "expiryTimestamp", allowlistedRequest.ExpiryTimestamp)
	return &AuthResult{
		workflowOwner: allowlistedRequest.Owner.Hex(),
		digest:        digestKey,
		expiresAt:     int64(allowlistedRequest.ExpiryTimestamp),
	}, nil
```
