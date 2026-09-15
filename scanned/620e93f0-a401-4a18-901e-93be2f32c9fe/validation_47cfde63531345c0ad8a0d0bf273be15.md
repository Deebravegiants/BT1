### Title
Unbounded memory growth in HTTP Trigger callback map lacks a size cap, unlike sibling caches - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Linux videobuf CVE-2010-5321 is a memory-consumption DoS caused by an unprivileged caller repeatedly triggering new allocations that are only reclaimed lazily, with no hard cap on outstanding allocations. The closest reachable analog in this codebase is `httpTriggerHandler.callbacks`, a map that grows once per user-submitted HTTP trigger request and is reclaimed only by a periodic, time-based reaper — with no maximum-size enforcement, unlike the structurally similar `capabilities/handler.go` cache.

### Finding Description
`httpTriggerHandler.HandleUserTriggerRequest` validates and authorizes an inbound request, then calls `setupCallback`, which unconditionally inserts a new entry into `h.callbacks[requestID]` after checking only for duplicate IDs, not overall map size: [1](#0-0) 

The only mechanisms bounding this map's size are:
1. `checkRateLimit`, a per-workflow-owner rate limiter [2](#0-1) 
2. `reapExpiredCallbacks`, a purely age-based cleanup that removes entries only after `CleanUpPeriodMs` has elapsed (default 10 minutes) [3](#0-2) [4](#0-3) 

Every entry carries a `responseAggregators` map (one per DON shard the workflow is assigned to) plus a `doneCh` channel, so each accepted request holds non-trivial state until the reaper's next sweep, not until the response completes and not bounded by total count. This mirrors the CVE's root cause: allocations from repeated caller-triggered operations accumulate faster than they are reclaimed, with reclamation gated by time/interval rather than a hard ceiling.

By contrast, the structurally near-identical (older) capability handler `capabilities/handler.go` explicitly guards against exactly this failure mode: it enforces both an age-based prune and a `MaxSavedCallbacks` size-based eviction (trimming to half the max when exceeded): [5](#0-4) 

The v2 HTTP trigger handler has no equivalent size cap on `h.callbacks`.

### Impact Explanation
An authenticated-but-unprivileged workflow caller (any client able to obtain a valid JWT for a registered workflow, i.e. any user of that workflow, not a gateway operator or node) can submit many trigger requests with distinct `requestID` values in a burst, each of which is only rejected on duplicate IDs, not on cache fullness. Since `checkRateLimit` throttles per-workflow-owner call rate rather than capping total outstanding (in-flight-or-unreaped) callbacks, and since the callbacks are only removed on the next `CleanUpPeriodMs` tick (default 10 minutes) or upon response completion, an attacker can accumulate a large number of live map entries (with attached aggregator state and channels) before the periodic reaper runs, causing elevated memory consumption on the gateway process serving that DON. This is a resource-exhaustion (denial of service) risk on the internet-facing gateway rather than a confidentiality/integrity break.

### Likelihood Explanation
Reaching this path requires only a valid JWT for a registered workflow (an ordinary workflow consumer, not an operator), then issuing HTTP trigger requests with unique `requestID`s faster than the workflow-owner rate limiter throttles them and faster than the reaper's cleanup interval. Whether this is practically exploitable depends on the configured `userRateLimiter` limits (not fully determined from the index) and `CleanUpPeriodMs`; if rate limits are generous or per-workflow-owner limits allow sustained throughput over a 10-minute window, growth could be significant. This is a plausible-but-moderate-severity condition given it depends on specific rate-limit configuration values I could not fully confirm from the available index.

### Recommendation
Add a maximum-size bound to `httpTriggerHandler.callbacks`, mirroring the `MaxSavedCallbacks`/`pruneCallbacks` pattern already used in `core/services/gateway/handlers/capabilities/handler.go`: when the map exceeds a configured threshold, evict the oldest unprocessed entries (or reject new requests with a limit-exceeded error) rather than relying solely on the time-based `reapExpiredCallbacks` sweep.

### Proof of Concept
1. Obtain a valid JWT authorized against a registered workflow (ordinary workflow-consumer privilege).
2. Repeatedly call the HTTP trigger method (`workflows.execute`) with unique `id` values, staying within the per-workflow-owner rate limit, for a duration approaching `CleanUpPeriodMs` (default 10 minutes).
3. Each accepted call adds an entry to `h.callbacks` via `setupCallback` [6](#0-5)  with no check against total map size, so the map grows unboundedly until the next periodic reap, unlike the sibling handler that caps size explicitly.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-455)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}

	// Build one response aggregator per shard the workflow is assigned to.
	assigned := h.workflowMetadataHandler.WorkflowShards(workflowID)
	if len(assigned) == 0 {
		// this shouldn't happen because we checked it in authorizeRequest()
		h.handleUserError(ctx, requestID, jsonrpc.ErrInternal, fmt.Sprintf("Workflow %s is not assigned to any DONs", workflowID), callback)
		return nil, errors.New("workflow is not assigned to any shards")
	}

	aggregators := make(map[string]*aggregation.IdenticalNodeResponseAggregator, len(assigned))
	for _, shard := range assigned {
		// (N+F)//2 + 1 threshold where N = number of nodes, F = number of faulty nodes
		threshold := (len(shard.members)+shard.f)/2 + 1
		agg, err := aggregation.NewIdenticalNodeResponseAggregator(threshold)
		if err != nil {
			return nil, errors.New("failed to create response aggregator: " + err.Error())
		}
		aggregators[shard.donID] = agg
	}

	doneCh := make(chan struct{})
	h.callbacks[requestID] = savedCallback{
		Callback:            callback,
		requestStartTime:    requestStartTime,
		createdAt:           time.Now(),
		responseAggregators: aggregators,
		doneCh:              doneCh,
	}
	return doneCh, nil
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L561-581)
```go
// reapExpiredCallbacks removes callbacks that are older than the maximum age
func (h *httpTriggerHandler) reapExpiredCallbacks(ctx context.Context) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	now := time.Now()
	var expiredCount int
	for reqID, callback := range h.callbacks {
		if now.Sub(callback.createdAt) > time.Duration(h.config.CleanUpPeriodMs)*time.Millisecond {
			if !callback.processed {
				h.metrics.IncrementRequestErrors(ctx, jsonrpc.ErrInternal, h.lggr)
			}
			h.cleanupCallback(reqID)
			expiredCount++
		}
	}
	if expiredCount > 0 {
		h.metrics.IncrementPendingRequestsCleanUpCount(ctx, int64(expiredCount), h.lggr)
		h.lggr.Infow("Removed expired callbacks", "count", expiredCount, "remaining", len(h.callbacks))
	}
	h.metrics.RecordPendingRequestsCount(ctx, int64(len(h.callbacks)), h.lggr)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L29-44)
```go
const (
	handlerName                          = "HTTPCapabilityHandler"
	defaultCleanUpPeriodMs               = 1000 * 60 * 10 // 10 minutes
	defaultMaxTriggerRequestDurationMs   = 1000 * 60      // 1 minute
	defaultNodeSendTimeoutMs             = 1000 * 10      // 10 seconds
	defaultInitialIntervalMs             = 100
	defaultMaxIntervalTimeMs             = 1000 * 30 // 30 seconds
	defaultMultiplier                    = 2.0
	defaultMetadataPullIntervalMs        = 1000 * 60 // 1 minute
	defaultMetadataAggregationIntervalMs = 1000 * 60 // 1 minute
	defaultMetadataPullRequestTimeoutMs  = 1000 * 30 // 30 seconds
	internalErrorMessage                 = "Internal server error occurred while processing the request"
	defaultOutboundRequestCacheTTLMs     = 1000 * 60 * 10      // 10 minutes
	defaultJWTReplayPeriodMs             = 1000 * 60 * 60 * 24 // 24 hours
	defaultSendResponseTimeoutMs         = 1000 * 5            // 5 seconds
)
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
