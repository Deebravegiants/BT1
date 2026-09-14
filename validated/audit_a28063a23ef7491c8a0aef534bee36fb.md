### Title
JWT replay protection is purely in-memory and resets on gateway restart/upgrade, allowing replay of previously-used tokens - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
The external report's root cause is that a contract's "state that decides how much a value should decay/reduce" (`lastSnapshotTimestamp`) is reset during `initialize()`/upgrade even though no real snapshot occurred, silently invalidating the anti-staleness/decay guarantee. The same root-cause pattern — an in-memory, process-lifetime-only state used to enforce a one-time-use / already-seen guarantee, which is wiped on process restart or upgrade — exists in the gateway's JWT replay-protection cache (`jwtReplayCache`) used by `WorkflowMetadataHandler.Authorize`.

### Finding Description
`WorkflowMetadataHandler` maintains a `jwtReplayCache` that records which JWT IDs (`jti`) have already been used, to prevent replay of a signed authorization token for HTTP-trigger workflow execution requests: [1](#0-0) 

```go
// jwtReplayCache manages used JWT IDs to prevent replay attacks
type jwtReplayCache struct {
	mu            sync.RWMutex
	cleanupPeriod time.Duration
	cache         map[string]time.Time // jti -> timestamp
}
```

This cache is a plain in-process `map`, constructed fresh every time a `WorkflowMetadataHandler` is created: [2](#0-1) 

The `Authorize` method checks the cache and rejects a duplicate JTI, but a JTI, once known, is only ever removed by TTL-based cleanup (`cleanupOldEntries`), not persisted anywhere: [3](#0-2) [4](#0-3) 

Because the map is held only in process memory, any gateway restart, redeploy, or contract-upgrade-style rollout of the gateway service (a new process is spun up with a brand-new `jwtReplayCache{}`) wipes the "already used" state — exactly analogous to the Tokemak bug where `lastSnapshotTimestamp` is reset on `initialize()` even though no real snapshot occurred, causing the protection mechanism to behave as if it had just been created with a clean slate. The `JWTReplayPeriodMs` (default 24h, see `defaultJWTReplayPeriodMs`) configuration implies JWTs can legitimately be valid/replay-checked over a long window: [5](#0-4) 

If a JWT-authorized HTTP-trigger request is captured by any observer during that up-to-24h window (e.g., logged, intercepted, or leaked) and the gateway process is restarted/redeployed in that window (a routine, frequent operational event for any long-lived service), the replay cache starts empty again and the previously-used JWT will pass the `isReplay` check and be accepted a second time, re-triggering the workflow execution for an unprivileged, external caller.

The same class of issue exists in `core/capabilities/vault/request_replay_guard.go`'s `RequestReplayGuard`, which is likewise a plain in-memory `map[string]int64` used to reject already-seen Vault request digests for both allowlist-based and JWT-based auth paths: [6](#0-5) 

Both are reachable from the internet-facing gateway/vault API on behalf of unprivileged external callers, matching the bug class of the external report: a protective, decay/expiry-tracking state that is not carried across process restarts and is silently reset, defeating the invariant it exists to enforce.

### Impact Explanation
An unprivileged actor who has captured a previously-submitted, validly-signed JWT-authorized request (or Vault request digest) can replay it after any gateway/vault-service restart or redeploy, causing:
- Re-execution of an HTTP-trigger workflow request that should only be processable once, potentially causing duplicate/unauthorized workflow runs.
- Re-acceptance of a previously consumed Vault request authorization, potentially allowing a stale/duplicated secrets operation to be re-applied.

This is a request-impersonation/authorization-bypass class issue (accepted category: "Accept only concrete authentication or role bypass ... request impersonation"), since the security property "each signed request/JWT can be used at most once" is silently violated whenever the process restarts, which is a routine and frequent event (deployments, crashes, node upgrades).

### Likelihood Explanation
Likelihood is moderate: it requires (1) an attacker/observer to have captured a previously-used, still-unexpired signed request (JWT or replay-guarded digest), and (2) a service restart/redeploy to occur within that token's validity/replay window (up to 24h by default for JWT replay). Given how frequently gateway nodes are redeployed/upgraded/restarted in operational environments, and that the replay window is configured on the order of hours, this is a realistic and reasonably likely occurrence, not a purely theoretical one.

### Recommendation
Persist replay/anti-replay state (the `jwtReplayCache` map and `RequestReplayGuard.seen` map) outside process memory — e.g., in a shared/persistent store (DB, Redis, or similar) keyed by JTI/digest with TTL — so that a restart or redeploy of the gateway/vault service does not reset previously-recorded "already used" markers. At minimum, do not treat process start as equivalent to "no requests have ever been seen"; if persistence is infeasible, document/bound the risk and ensure JWT/replay-guard expiry windows are short enough that the operational restart cadence cannot plausibly outlast them.

### Proof of Concept
1. An unprivileged client sends a JWT-authorized HTTP-trigger request to the gateway; `WorkflowMetadataHandler.Authorize` records the JTI in `jwtCache` via `recordUsage`.
2. An observer/attacker captures this same signed request/JWT (e.g., from logs, a MITM'd but still-valid channel, or a previously-authorized but replayed transport).
3. The gateway process is restarted (deployment, crash-restart, scaling event) — `NewWorkflowMetadataHandler` recreates an empty `jwtReplayCache` per [7](#0-6) .
4. The attacker resubmits the exact same JWT-authorized request. `isReplay(claims.ID)` returns `false` because the JTI is no longer present in the fresh, empty cache, so `Authorize` succeeds and the workflow-trigger request is processed a second time — reproducing the "state incorrectly reset after restart/upgrade" bug class from the external report.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L29-34)
```go
// jwtReplayCache manages used JWT IDs to prevent replay attacks
type jwtReplayCache struct {
	mu            sync.RWMutex
	cleanupPeriod time.Duration
	cache         map[string]time.Time // jti -> timestamp
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L56-77)
```go
// NewWorkflowMetadataHandler creates a new WorkflowMetadataHandler spanning the
// full DON×shard matrix. Each shard gets its own aggregator with threshold F+1.
func NewWorkflowMetadataHandler(lggr logger.Logger, cfg ServiceConfig, shards []*shardEndpoint, nodeAddrToShard map[string]*shardEndpoint, metrics *metrics.Metrics) *WorkflowMetadataHandler {
	aggs := make(map[string]*aggregation.WorkflowMetadataAggregator, len(shards))
	for _, shard := range shards {
		threshold := shard.f + 1
		aggs[shard.donID] = aggregation.NewWorkflowMetadataAggregator(lggr, threshold, time.Duration(cfg.CleanUpPeriodMs)*time.Millisecond, metrics)
	}
	return &WorkflowMetadataHandler{
		lggr:            logger.Named(lggr, "HTTPTriggerWorkflowMetadataHandler"),
		authorizedKeys:  make(map[string]map[gateway.AuthorizedKey]struct{}),
		workflowRefToID: make(map[workflowReference]string),
		workflowIDToRef: make(map[string]workflowReference),
		workflowShards:  make(map[string][]*shardEndpoint),
		aggs:            aggs,
		shards:          shards,
		nodeAddrToShard: nodeAddrToShard,
		config:          cfg,
		stopCh:          make(services.StopChan),
		metrics:         metrics,
		jwtCache:        newJWTReplayCache(time.Duration(cfg.JWTReplayPeriodMs) * time.Millisecond),
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-107)
```go
func (h *WorkflowMetadataHandler) Authorize(workflowID string, token string, req *jsonrpc.Request[json.RawMessage]) (*gateway.AuthorizedKey, error) {
	claims, signer, err := utils.VerifyRequestJWT(token, *req)
	if err != nil {
		h.lggr.Errorw("Failed to verify JWT", "error", err)
		return nil, err
	}

	if h.jwtCache.isReplay(claims.ID) {
		h.lggr.Warnw("JWT token has already been used", "workflowID", workflowID, "signer", signer.Hex(), "jti", claims.ID)
		return nil, errors.New("JWT token has already been used. Please generate a new one with new id (jti)")
	}

	keys, exists := h.authorizedKeys[workflowID]
	if !exists {
		h.lggr.Errorw("Workflow ID not found in authorized keys", "workflowID", workflowID)
		return nil, fmt.Errorf("workflow ID %s not found", workflowID)
	}
	key := gateway.AuthorizedKey{
		KeyType:   gateway.KeyTypeECDSAEVM,
		PublicKey: strings.ToLower(signer.Hex()),
	}
	if _, exists = keys[key]; !exists {
		h.lggr.Errorw("Signer not found in authorized keys", "signer", signer.Hex())
		return nil, fmt.Errorf("signer '%s' is not authorized for workflow '%s'. Ensure that the signer is registered in the workflow definition", signer.Hex(), workflowID)
	}
	h.jwtCache.recordUsage(claims.ID)

	return &key, nil
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L392-426)
```go
func newJWTReplayCache(cleanupPeriod time.Duration) *jwtReplayCache {
	return &jwtReplayCache{
		cache:         make(map[string]time.Time),
		cleanupPeriod: cleanupPeriod,
	}
}

func (cache *jwtReplayCache) isReplay(jti string) bool {
	cache.mu.RLock()
	defer cache.mu.RUnlock()

	_, exists := cache.cache[jti]
	return exists
}

func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}

// cleanupOldEntries removes expired entries from the cache
func (cache *jwtReplayCache) cleanupOldEntries(cutoff time.Time) int {
	cache.mu.Lock()
	defer cache.mu.Unlock()
	var expiredCount int
	for jti, createdAt := range cache.cache {
		if createdAt.Before(cutoff) {
			delete(cache.cache, jti)
			expiredCount++
		}
	}
	return expiredCount
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L42-42)
```go
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
```

**File:** core/capabilities/vault/request_replay_guard.go (L16-28)
```go
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
