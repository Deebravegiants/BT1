Note: `authorizeRequest` is called before `checkRateLimit`, meaning `WorkflowMetadataHandler.Authorize()` (which unconditionally inserts into `jwtCache.cache` via `recordUsage`) executes on every valid-JWT request prior to any rate limiting. The rate limiter only gates the trigger dispatch step, not JWT-cache insertion.

### Title
Unbounded growth of the JWT replay-protection cache in `WorkflowMetadataHandler` leads to memory-exhaustion DoS - ([File: core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go])

### Summary
`jwtReplayCache`, used by the HTTP Trigger gateway handler to prevent JWT replay, has no maximum size and is only pruned once per `JWTReplayPeriodMs` (default 24 hours). Every authenticated HTTP trigger request permanently adds an entry to this in-memory map until the next cleanup tick, regardless of rate limiting, giving an authorized-but-unprivileged caller (any external client holding a workflow's registered signer key) an unbounded, cheap way to grow gateway memory for up to 24 hours.

### Finding Description
`WorkflowMetadataHandler.Authorize` is invoked from `httpTriggerHandler.authorizeRequest`, which runs before `checkRateLimit` in `HandleUserTriggerRequest`: [1](#0-0) 

`Authorize` calls `h.jwtCache.recordUsage(claims.ID)` for every request whose JWT signature verifies and whose signer is authorized for the workflow: [2](#0-1) 

`recordUsage` unconditionally writes into the map with no cap check, unlike the sibling `RequestCache` type elsewhere in the gateway package which enforces an explicit `maxCacheSize`: [3](#0-2) [4](#0-3) 

The only pruning mechanism is a ticker whose period equals `cleanupPeriod` (`JWTReplayPeriodMs`, default 24h): [5](#0-4) [6](#0-5) 

Since each `jti` value is caller-chosen (part of the JWT claims) and only needs to be unique to pass the replay check, a single authorized caller can generate an arbitrary number of distinct, validly signed JWTs (cheap to produce once holding the signer's private key) and submit them in rapid succession. `checkRateLimit` is applied only after `Authorize`/`recordUsage` has already executed, so per-workflow rate limits do not bound the number of cache insertions that occur before a request is rejected downstream — rate limiting throttles execution dispatch, not JWT-cache growth. This breaks the implicit invariant (mirrored by the analogous bounded `RequestCache.maxCacheSize`) that gateway-facing per-request caches must be size-bounded, allowing unbounded map growth analogous to the reported Solidity `tranches` array growing past its intended bound.

### Impact Explanation
An authorized workflow caller (not requiring any DON/operator privilege, only knowledge of a signer key already permitted to trigger a specific workflow) can inflate the `jwtReplayCache` map to a large size within the up-to-24-hour window before cleanup, consuming gateway process memory and CPU (map operations degrade under load, mutex contention on `jwtCache.mu` increases). This can degrade or crash the gateway service, impacting all workflows and DON members that route through it — a availability/DoS impact on shared infrastructure. This is a genuine authorized-caller path (not malicious-node or operator-only), reachable directly from the internet-facing HTTP trigger endpoint.

### Likelihood Explanation
Likelihood is moderate: it requires possession of a legitimate signer key authorized for at least one deployed workflow (i.e., the caller must be an intended user of that workflow's HTTP trigger, not an arbitrary internet stranger), but no special node/operator access is needed, and generating many uniquely-`jti` signed JWTs is computationally trivial once the key is held. The default 24-hour cleanup window and lack of any cap make sustained abuse straightforward to reach memory pressure before the periodic prune runs.

### Recommendation
Add an explicit maximum size to `jwtReplayCache` (mirroring `requestCache.maxCacheSize`), rejecting/evicting-oldest when the cap is exceeded, and/or shorten the effective cleanup granularity independent of `JWTReplayPeriodMs` (e.g., sweep more frequently while still honoring the full replay window per entry via per-entry TTL rather than a single global cleanup pass). Additionally, consider enforcing per-workflow-owner limits on JWT cache insertions before `recordUsage`, not only on trigger dispatch, so a single authorized caller cannot unboundedly grow the cache irrespective of the downstream rate limiter.

### Proof of Concept
Not independently executable from this environment (no filesystem/terminal access), but the exploitable path is:
1. Obtain (or be) an authorized signer for any workflow with an HTTP trigger registered on the gateway (`authorizedKeys` populated via `syncMetadata`) — [7](#0-6) 
2. Repeatedly send `workflows.execute` JSON-RPC requests to the gateway's HTTP trigger endpoint, each with a validly ECDSA-signed JWT containing a freshly generated unique `jti` claim, targeting the same (or different) authorized workflow(s).
3. Each request causes `Authorize` → `recordUsage(claims.ID)` to add a new entry to `jwtCache.cache` — [8](#0-7)  — before any rate-limit check can reject it.
4. Because cleanup only runs once per `JWTReplayPeriodMs` (default 24h) — [9](#0-8)  — the cache grows without bound for the duration of that window, proportional to the number of distinct requests sent.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L114-183)
```go
func (h *WorkflowMetadataHandler) syncMetadata(ctx context.Context) {
	authorizedKeys := make(map[string]map[gateway.AuthorizedKey]struct{})
	workflowRefToID := make(map[workflowReference]string)
	workflowIDToRef := make(map[string]workflowReference)
	workflowShards := make(map[string][]*shardEndpoint)

	for _, shard := range h.shards {
		agg := h.aggs[shard.donID]
		metadata := agg.Aggregate()
		for _, data := range metadata {
			workflowID := data.WorkflowSelector.WorkflowID
			workflowRef := workflowReference{
				workflowOwner: data.WorkflowSelector.WorkflowOwner,
				workflowName:  data.WorkflowSelector.WorkflowName,
				workflowTag:   data.WorkflowSelector.WorkflowTag,
			}

			// Case 1: this workflow ID was already registered. If the reference
			// matches, this is the same workflow reported by another shard —
			// append the shard to its fan-out list. If the reference differs,
			// it's a conflicting observation; drop it.
			if existingRef, idExists := workflowIDToRef[workflowID]; idExists {
				if existingRef == workflowRef {
					workflowShards[workflowID] = append(workflowShards[workflowID], shard)
				} else {
					h.lggr.Debugw("Duplicate workflow ID with conflicting reference, dropping",
						"workflowID", workflowID, "existingRef", existingRef, "conflictingRef", workflowRef)
				}
				continue
			}

			// Case 2: this workflow reference was already registered under a
			// different workflow ID. First-wins by reference; drop the duplicate.
			if _, refExists := workflowRefToID[workflowRef]; refExists {
				h.lggr.Debugw("Duplicate workflow reference found, dropping",
					"workflowRef", workflowRef, "workflowID", workflowID)
				continue
			}

			// Case 3: new workflow ID and reference — register it.
			workflowIDToRef[workflowID] = workflowRef
			workflowRefToID[workflowRef] = workflowID
			authorizedKeys[workflowID] = make(map[gateway.AuthorizedKey]struct{})
			for _, key := range data.AuthorizedKeys {
				authorizedKeys[workflowID][key] = struct{}{}
			}
			workflowShards[workflowID] = append(workflowShards[workflowID], shard)
		}
	}

	h.mu.Lock()
	defer h.mu.Unlock()

	if len(h.workflowIDToRef) == 0 && len(workflowIDToRef) > 0 {
		latencyMs := time.Since(h.startTime).Milliseconds()
		h.metrics.RecordMetadataSyncStartupLatency(ctx, latencyMs, h.lggr)
	}
	// Log all registered workflow IDs
	workflowIDs := make([]string, 0, len(workflowIDToRef))
	for workflowID := range workflowIDToRef {
		workflowIDs = append(workflowIDs, workflowID)
	}
	h.lggr.Debugw("Synced workflow metadata", "workflowIDs", workflowIDs, "count", len(workflowIDs))

	h.authorizedKeys = authorizedKeys
	h.workflowRefToID = workflowRefToID
	h.workflowIDToRef = workflowIDToRef
	h.workflowShards = workflowShards
	h.metrics.RecordLoadedMetadataSize(ctx, int64(len(h.workflowIDToRef)), h.lggr)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L298-304)
```go
		h.runTicker(h.jwtCache.cleanupPeriod, func(ctx context.Context) {
			now := time.Now()
			expiredCount := h.jwtCache.cleanupOldEntries(now.Add(-h.jwtCache.cleanupPeriod))
			h.metrics.IncrementJwtCacheCleanUpCount(ctx, int64(expiredCount), h.lggr)
			h.metrics.RecordJwtCacheSize(ctx, int64(len(h.jwtCache.cache)), h.lggr)
			h.lggr.Debugw("Workflow execution cache cleanup completed", "expired_entries", expiredCount, "remaining_entries", len(h.jwtCache.cache))
		})
```

**File:** core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go (L407-412)
```go
func (cache *jwtReplayCache) recordUsage(jti string) {
	cache.mu.Lock()
	defer cache.mu.Unlock()

	cache.cache[jti] = time.Now()
}
```

**File:** core/services/gateway/handlers/common/requestcache.go (L46-66)
```go
func NewRequestCache[T any](timeout time.Duration, maxCacheSize uint32) RequestCache[T] {
	return &requestCache[T]{cache: make(map[globalID]*pendingRequest[T]), timeout: timeout, maxCacheSize: maxCacheSize}
}

func (c *requestCache[T]) NewRequest(lggr logger.Logger, request *api.Message, callback handlers.Callback, responseData *T) error {
	if request == nil {
		return errors.New("request is nil")
	}
	if responseData == nil {
		return errors.New("responseData is nil")
	}
	key := globalID{request.Body.Sender, request.Body.MessageID}
	c.mu.Lock()
	defer c.mu.Unlock()
	_, ok := c.cache[key]
	if ok {
		return errors.New("request already exists")
	}
	if len(c.cache) >= int(c.maxCacheSize) {
		return errors.New("request cache is full")
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L41-42)
```go
	defaultOutboundRequestCacheTTLMs     = 1000 * 60 * 10      // 10 minutes
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
```
