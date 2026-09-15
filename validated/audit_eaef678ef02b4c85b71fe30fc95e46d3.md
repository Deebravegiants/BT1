The claim's core technical assertions are accurate and verified in the code: `setupCallback` only checks for duplicate `requestID`, never total map size, before inserting into `h.callbacks`, and `reapExpiredCallbacks` is purely time-based (default `CleanUpPeriodMs` = 10 minutes), with no `MaxSavedCallbacks`-style cap as exists in the sibling `capabilities/handler.go`.Audit Report

## Title
Unbounded memory growth in HTTP Trigger callback map lacks a size cap, unlike sibling caches - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

## Summary
`httpTriggerHandler.callbacks` grows by one entry per accepted HTTP trigger request via `setupCallback`, which only rejects duplicate `requestID`s and never checks total map size before inserting. Reclamation happens solely through `reapExpiredCallbacks`, a time-based sweep gated by `CleanUpPeriodMs` (default 10 minutes), with no `MaxSavedCallbacks`-style eviction like the structurally similar `capabilities/handler.go`.

## Finding Description
The request flow in `HandleUserTriggerRequest` validates and authorizes the request, checks `checkRateLimit` (a per-workflow-owner limiter scoped via `settings.ScopeWorkflow`), and then unconditionally calls `setupCallback`, which inserts a new `savedCallback{}` entry (containing a `responseAggregators` map per DON shard plus a `doneCh` channel) into `h.callbacks[requestID]` after only checking for ID collision: [1](#0-0)  The only cleanup path is `reapExpiredCallbacks`, which removes entries strictly based on age (`CleanUpPeriodMs`, defaulting to 10 minutes), not on map size: [2](#0-1) [3](#0-2)  By contrast, the older sibling `capabilities/handler.go` explicitly caps saved-callback growth with both age-based pruning and a hard `MaxSavedCallbacks` eviction that trims to half the max when exceeded: [4](#0-3)  The v2 HTTP trigger handler has no equivalent size-based bound.

## Impact Explanation
This is a legitimate structural gap: an authenticated workflow consumer (holder of a valid JWT for a registered workflow) can submit trigger requests with unique `requestID`s, each of which is only throttled by a per-workflow-owner rate limiter (`checkRateLimit`, scope `settings.ScopeWorkflow`) rather than a cap on total outstanding/unreaped callbacks. [5](#0-4)  Because reclamation only occurs at the next `CleanUpPeriodMs` tick (10 minutes by default) or upon response completion, sustained throughput within the rate limit over that window can accumulate map entries carrying non-trivial state (per-shard aggregators, channels), increasing gateway memory usage. This maps to a resource-exhaustion / denial-of-service risk on the gateway process, which is a legitimate but bounded-severity concern — it does not by itself grant unauthorized access, data exfiltration, or fund movement.

## Likelihood Explanation
Exploitability depends entirely on the configured rate limits for `userRateLimiter` (scope: workflow owner), which were not fully determinable from the available index — I could not locate the concrete default rate/burst values or the `RateLimiter` construction/configuration wiring for this specific limiter within the codebase search performed. Without confirming that the per-workflow-owner rate limit is generous enough (or configurable to be generous enough) to allow a meaningfully large number of requests within a 10-minute window, the actual severity of the accumulation cannot be concretely quantified. The report itself acknowledges this same uncertainty ("depends on specific rate-limit configuration values I could not fully confirm from the available index").

## Recommendation
Add a maximum-size bound to `httpTriggerHandler.callbacks`, mirroring the `MaxSavedCallbacks` / `pruneCallbacks` pattern in `core/services/gateway/handlers/capabilities/handler.go`: when the map exceeds a configured threshold, evict oldest unprocessed entries or reject new requests with a limit-exceeded error, rather than relying solely on the time-based `reapExpiredCallbacks` sweep.

## Proof of Concept
1. Obtain a valid JWT authorized against a registered workflow (ordinary workflow-consumer privilege, no operator/admin role required).
2. Repeatedly invoke the `workflows.execute` HTTP trigger method with unique `id` values, staying within the per-workflow-owner rate limit enforced by `checkRateLimit`, for a duration approaching `CleanUpPeriodMs` (default 10 minutes).
3. Observe (e.g., via `h.metrics.RecordPendingRequestsCount` in `reapExpiredCallbacks`) that `len(h.callbacks)` grows without any size-based rejection, unlike the equivalent test that would be expected against `capabilities/handler.go`'s `MaxSavedCallbacks` enforcement.
4. Confirming the real-world severity of this PoC requires knowledge of the configured `userRateLimiter` throughput limits, which was not verifiable from the indexed code.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-426)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
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
