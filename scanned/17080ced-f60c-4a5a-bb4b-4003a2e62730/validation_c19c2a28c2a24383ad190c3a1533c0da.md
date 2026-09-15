Confirmed: `authorizeRequest` (called via `HandleUserTriggerRequest`, at `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:368-376`) calls `h.workflowMetadataHandler.Authorize` **before** the per-workflow rate limit is checked (`checkRateLimit` runs afterward at line 111 of `HandleUserTriggerRequest`). This confirms the JWT is verified and a unique-`jti` cache entry is recorded prior to any throttling, and the `jwtReplayCache` is a single global unbounded map cleaned only once every `JWTReplayPeriodMs` (default 24h).

### Title
Unbounded JWT-replay cache growth in `WorkflowMetadataHandler.Authorize` enables gateway memory-exhaustion DoS - (File: `core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go`)

### Summary
The HTTP-trigger gateway path authorizes each incoming request by verifying a JWT and recording its `jti` in a single in-memory map, `jwtReplayCache.cache`, to block replay. This map has no maximum-size bound and is only pruned by a periodic cleanup ticker that runs once per `JWTReplayPeriodMs` (default 24 hours). Any caller holding a validly-signed JWT for an authorized workflow key can trigger unbounded growth of this shared map simply by sending unique `jti` values, exactly analogous to the reported Solidity issue where an unbounded `EnumerableSet` grows via cheap, repeated user actions and eventually causes resource-exhaustion/DoS on the routine that must scan it.

### Finding Description
`WorkflowMetadataHandler.Authorize` is the gateway-side authorization entry point for HTTP trigger requests: [1](#0-0) 

It calls `h.jwtCache.isReplay(claims.ID)` and, on success, `h.jwtCache.recordUsage(claims.ID)`, unconditionally inserting into the shared `map[string]time.Time`: [2](#0-1) 

The cache is only pruned by a ticker keyed to `cleanupPeriod`, which is set from `cfg.JWTReplayPeriodMs`, defaulting to 24 hours: [3](#0-2) [4](#0-3) 

Critically, `HandleUserTriggerRequest` calls `authorizeRequest` (which invokes `Authorize` and records the `jti`) *before* `checkRateLimit`: [5](#0-4) 

So the map insertion is not throttle-gated at all — the per-workflow-owner rate limiter in `checkRateLimit` only applies to steps executed after the JWT has already been recorded: [6](#0-5) 

Any holder of a legitimately signed JWT for an authorized key of any registered workflow (an unprivileged client of the gateway, not an operator or node) can mint an arbitrary number of unique `jti` values (trivial, since `jti` is attacker-controlled at signing time) and issue requests as fast as the gateway will accept them over a 24-hour window before the cleanup ticker fires. Each request inserts one entry into the global, unbounded `jwtReplayCache.cache` map, growing gateway process memory and the cost of the periodic `cleanupOldEntries` full-map scan, which holds `cache.mu` for the duration of the scan on every one of the periodic ticks: [7](#0-6) 

This is a structurally identical bug class to the reported `accruePremiumAndExpireProtections` DDoS: an unbounded, shared collection that grows per unprivileged-actor request and is periodically iterated in full, with no size cap — only a time-based reset far too infrequent (24h) to bound worst-case growth.

### Impact Explanation
Unbounded growth of a shared, mutex-protected map used by every HTTP-trigger authorization degrades and can eventually exhaust gateway memory, and the periodic full-map `cleanupOldEntries` scan (holding the cache's lock) becomes progressively more expensive as the map grows, blocking concurrent `isReplay`/`recordUsage` calls for the whole gateway (all workflows, not just the attacker's). Because the cache is shared across all workflows rather than scoped per-owner, one authorized workflow-signing key is enough to degrade authorization performance/availability for the whole HTTP trigger gateway path — a cross-tenant availability impact from a single unprivileged (from the gateway's perspective, merely "authorized-for-one-workflow") caller.

### Likelihood Explanation
Likelihood is high: the only prerequisite is possession of one valid signing key authorized for any registered workflow (a normal, non-privileged workflow-owner credential, not an operator/node secret), and the attacker fully controls the `jti` claim, so producing unique values costs nothing. The rate limiter that exists in this path is applied only after the JWT has already been recorded in the unbounded cache, so it does not bound cache growth — it only limits how many *trigger executions* are forwarded to the DON, not how many entries are inserted into `jwtCache`.

### Recommendation
- Bound `jwtReplayCache` with a maximum entry count (evict oldest/LRU on overflow) independent of the time-based `cleanupPeriod`, similar to the size cap already used in `core/services/gateway/handlers/common/requestcache.go`'s `NewRequestCache(ttl, maxSize)`.
- Move (or duplicate) the rate-limit check before JWT verification/`recordUsage`, or apply a lightweight per-signer/per-workflow quota specifically gating cache insertion.
- Reduce the default `JWTReplayPeriodMs` cleanup interval, or run incremental/amortized cleanup instead of a single full-map lock-and-scan, to reduce worst-case memory and lock-hold time.

### Proof of Concept
1. Obtain (or be) an authorized signer for any single registered workflow (a normal client credential for that workflow, not privileged infrastructure access).
2. Repeatedly call the HTTP trigger endpoint (`workflows.execute` via the gateway) with a validly signed JWT whose `jti` claim is a new random value on every request, targeting that workflow.
3. Each call passes `Authorize` (`core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go:80-108`), inserting into `jwtCache.cache` before `checkRateLimit` runs.
4. Sustaining this for a fraction of the 24-hour default `JWTReplayPeriodMs` window accumulates a very large number of entries in `jwtCache.cache`, growing gateway memory usage and increasing the lock-held duration of the next `cleanupOldEntries` scan, degrading authorization latency/availability for all workflows sharing the gateway.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L80-108)
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
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L280-304)
```go
// Start begins the periodic pull loop.
func (h *WorkflowMetadataHandler) Start(ctx context.Context) error {
	return h.StartOnce("WorkflowMetadataHandler", func() error {
		h.lggr.Info("Starting HTTP Trigger Metadata Handler")
		h.startTime = time.Now()
		for _, shard := range h.shards {
			if err := h.aggs[shard.donID].Start(ctx); err != nil {
				return fmt.Errorf("failed to start aggregator for shard %s: %w", shard.donID, err)
			}
		}
		h.runTicker(time.Duration(h.config.MetadataPullIntervalMs)*time.Millisecond, func(ctx context.Context) {
			err2 := h.sendMetadataPullRequest()
			if err2 != nil {
				h.lggr.Errorw("Failed to send pull request", "error", err2)
			}
		})
		h.runTicker(time.Duration(h.config.MetadataAggregationIntervalMs)*time.Millisecond, h.syncMetadata)

		h.runTicker(h.jwtCache.cleanupPeriod, func(ctx context.Context) {
			now := time.Now()
			expiredCount := h.jwtCache.cleanupOldEntries(now.Add(-h.jwtCache.cleanupPeriod))
			h.metrics.IncrementJwtCacheCleanUpCount(ctx, int64(expiredCount), h.lggr)
			h.metrics.RecordJwtCacheSize(ctx, int64(len(h.jwtCache.cache)), h.lggr)
			h.lggr.Debugw("Workflow execution cache cleanup completed", "expired_entries", expiredCount, "remaining_entries", len(h.jwtCache.cache))
		})
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L392-412)
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
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L414-426)
```go
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L41-42)
```go
	defaultOutboundRequestCacheTTLMs     = 1000 * 60 * 10      // 10 minutes
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-113)
```go
func (h *httpTriggerHandler) HandleUserTriggerRequest(ctx context.Context, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback, requestStartTime time.Time) error {
	triggerReq, err := h.validatedTriggerRequest(ctx, req, callback)
	if err != nil {
		return err
	}

	workflowID, err := h.resolveWorkflowID(ctx, triggerReq, req.ID, callback)
	if err != nil {
		return err
	}

	key, err := h.authorizeRequest(ctx, workflowID, req, callback)
	if err != nil {
		return err
	}

	if err = h.checkRateLimit(ctx, workflowID, req.ID, callback); err != nil {
		return err
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L392-417)
```go
func (h *httpTriggerHandler) checkRateLimit(ctx context.Context, workflowID, requestID string, callback handlers.Callback) error {
	workflowRef, found := h.workflowMetadataHandler.GetWorkflowReference(workflowID)
	if !found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "workflow reference not found", callback)
		return errors.New("workflow reference not found")
	}

	orgID := h.resolveOrgID(ctx, workflowRef.workflowOwner)
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: workflowRef.workflowOwner, Org: orgID, Workflow: workflowID})
	if err := h.userRateLimiter.AllowErr(ctx); err != nil {
		lggr := logger.With(h.lggr, platform.KeyWorkflowID, workflowID, platform.KeyWorkflowOwner, workflowRef.workflowOwner, "requestID", requestID, "err", err)
		if errLimited, ok := errors.AsType[limits.ErrorRateLimited](err); ok {
			switch errLimited.Scope {
			case settings.ScopeWorkflow:
				lggr.Errorf("failed to start execution: per workflow rate limit exceeded")
				h.metrics.IncrementWorkflowThrottled(ctx, h.lggr)
			default:
				lggr.Errorf("failed to start execution: unexpected rate limit for scope %s", errLimited.Scope)
			}
			h.handleUserError(ctx, requestID, jsonrpc.ErrLimitExceeded, "rate limit exceeded", callback)
			return err
		}
		return fmt.Errorf("failed to check rate limit: %w", err)
	}
	return nil
}
```
