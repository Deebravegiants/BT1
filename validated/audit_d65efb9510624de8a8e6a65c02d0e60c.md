### Title
Unbounded in-memory callback map in the HTTP Trigger Gateway handler enables authenticated workflow-owner DoS - (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The Gateway's `httpTriggerHandler` keeps one entry per in-flight request in `h.callbacks` (keyed by `requestID`), but unlike the sibling legacy handler (`core/services/gateway/handlers/capabilities/handler.go`), which enforces a `MaxSavedCallbacks` hard cap in addition to a time-based reaper, the v2 HTTP trigger handler only removes entries via time-based reaping (`reapExpiredCallbacks`). There is no cap on the number of concurrently pending entries.

### Finding Description
`setupCallback` inserts a new `savedCallback` into `h.callbacks[requestID]` for every accepted trigger request, guarding only against a duplicate `requestID` for the same in-flight request: [1](#0-0) 

The only reclamation mechanism is `reapExpiredCallbacks`, which is purely time based (`CleanUpPeriodMs`) and contains no size/count cap: [2](#0-1) 

This is materially different from the legacy `capabilities/handler.go`, which explicitly caps the number of saved callbacks (`MaxSavedCallbacks`) in addition to age-based expiry, precisely to bound memory usage: [3](#0-2) 

The only throttle on the v2 path is `checkRateLimit`, which is a per-workflow rate limiter (`settings.ScopeWorkflow`) rather than a bound on total outstanding/pending callback entries: [4](#0-3) 

Because each `savedCallback` carries a `responseAggregators` map (one `IdenticalNodeResponseAggregator` per shard the workflow is assigned to) plus a `doneCh` channel and the full request context, an authenticated workflow owner who is under the per-workflow rate limit but issues a sustained stream of unique `requestID`s can keep accumulating entries in `h.callbacks` for up to `CleanUpPeriodMs` before they're reaped, and the entries are never trimmed to a hard ceiling the way the legacy handler's are. This mirrors the Authorino CVE-2025-25207 pattern of an authenticated-but-lower-privileged actor (a workflow/dev persona, not a node operator) causing unbounded server-side resource accumulation because the callback bookkeeping structure lacks a maximum-size bound and only has a time-based reaper, all enforced on a single Gateway process instance.

### Impact Explanation
If an authenticated workflow owner sustains request volume near/at the per-workflow rate limit threshold across the `CleanUpPeriodMs` window (and especially if that workflow is assigned to many shards, inflating the per-entry `responseAggregators` map size), the `httpTriggerHandler.callbacks` map can grow large enough to pressure Gateway process memory/CPU, degrading or denying trigger processing for all workflows served by that Gateway/DON member — a single-instance service exactly as described in the advisory. This is impact only, not confirmed exploitable at scale without knowing the deployed rate-limit configuration values.

### Likelihood Explanation
Likelihood depends heavily on operator-configured rate limit thresholds (`userRateLimiter` settings) and `CleanUpPeriodMs`/`MaxTriggerRequestDurationMs` values, which are not visible in this snippet-level review. If the workflow-scope rate limit is generous (e.g., high burst/refill) relative to the cleanup period, sustained legitimate-looking traffic from one workflow owner could realistically accumulate a large number of pending callback entries before reaping runs.

### Recommendation
Add an explicit maximum-size bound (analogous to `MaxSavedCallbacks` in `core/services/gateway/handlers/capabilities/handler.go`) to `httpTriggerHandler.callbacks`, evicting oldest/least-relevant entries once the cap is exceeded, independent of the time-based reaper and independent of per-workflow rate limiting.

### Proof of Concept
Not independently verified against a running deployment; this analysis is based on static code review of `setupCallback`/`reapExpiredCallbacks` versus the capped implementation in `capabilities/handler.go`. Confirming actual exploitability requires knowing the deployed `userRateLimiter` configuration and `CleanUpPeriodMs`, which are not available in this review.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-456)
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
}
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
