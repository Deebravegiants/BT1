Audit Report

## Title
Cross-workflow request-ID squatting causes denial of service in the CRE Gateway HTTP Trigger Handler - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

## Summary
The gateway's HTTP trigger handler stores in-flight requests in a single map keyed only by the client-supplied `requestID`, with no per-workflow namespacing, verified at [1](#0-0) . Any authorized workflow can occupy an arbitrary `requestID` for up to the reaper interval (default 10 minutes), causing any other workflow's legitimate request using the same ID to be rejected immediately with `jsonrpc.ErrConflict`.

## Finding Description
`setupCallback` checks for a pre-existing entry keyed purely by `requestID` and returns an error/conflict response if found, without any consideration of which workflow owns the slot: [2](#0-1) . The only validation performed on the client-supplied `requestID` is a non-empty check and a check that it doesn't contain `/`: [3](#0-2) . `HandleUserTriggerRequest` resolves and authorizes the target `workflowID` before calling `setupCallback`, but the `workflowID` parameter is only used to build response aggregators for that workflow's assigned shards — it is never combined with `requestID` to form the map key: [4](#0-3) . Rate limiting is scoped per-workflow via `contexts.CRE{...Workflow: workflowID}`, not globally, so it does not prevent one workflow from exhausting the shared ID namespace: [5](#0-4) . The occupied slot is released only when the callback completes or via the periodic reaper running on `CleanUpPeriodMs` (default 10 minutes, `defaultCleanUpPeriodMs = 1000 * 60 * 10`): [6](#0-5) . No existing check (auth, rate limiting, ID validation) mitigates the cross-workflow collision because none of them account for workflow scoping in the shared map key.

## Impact Explanation
A workflow authorized against the gateway can deny another, unrelated workflow's HTTP-triggered executions by squatting on the same `requestID`, since the in-flight map is process-global rather than scoped per workflow. Colliding requests are rejected outright with `ErrConflict` and never reach the DON, which is a genuine availability/logic defect for a multi-tenant gateway, though it is a resource-contention/DoS-class issue rather than data corruption, fund movement, or authentication bypass. The practical blast radius is limited to requests that happen to collide on the same string ID, and the effect self-heals after at most `CleanUpPeriodMs` (10 minutes by default).

## Likelihood Explanation
Exploitability requires the attacker to control an authorized workflow (a comparatively low bar, since workflow authorization only requires a valid signing key per `WorkflowMetadataHandler.Authorize`) and to predict or brute-force a victim's `requestID` values, which are client-chosen strings restricted only by "must not contain `/`." Predictable ID schemes (timestamps, counters) make collisions plausible in practice, and per-workflow rate limits (default burst 50 / 5 rps) still allow squatting many IDs within a 10-minute window.

## Recommendation
Scope the in-flight callback map key by `(workflowID, requestID)` rather than `requestID` alone so that one workflow cannot occupy or interfere with another workflow's request-ID namespace. Additionally, consider capping the number of concurrently in-flight callbacks a single workflow/owner may hold to further reduce the abuse window.

## Proof of Concept
1. Attacker registers/owns Workflow A and obtains a valid `AuthorizedKey` via `WorkflowMetadataHandler.Authorize`.
2. Attacker submits a `workflows.execute` (`MethodWorkflowExecute`) trigger request to the gateway with `id = "X"`, properly signed for Workflow A. `setupCallback` inserts `h.callbacks["X"]`.
3. Victim's Workflow B submits a legitimate trigger request using the same `id = "X"`. `setupCallback` finds `h.callbacks["X"]` already occupied and immediately returns `jsonrpc.ErrConflict` ("in-flight request ID"), denying Workflow B's execution.
4. Workflow B's request with ID `"X"` continues to fail until Workflow A's request completes or is reaped (up to `defaultCleanUpPeriodMs` = 10 minutes), after which Attacker can repeat with new candidate IDs.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L64-65)
```go
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L141-146)
```go
	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
	}

	return h.sendWithRetries(ctx, legacyExecutionID, executionIDWithTriggerIndex, reqWithKey, workflowID, doneCh)
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L190-202)
```go
func (h *httpTriggerHandler) validateRequestID(ctx context.Context, requestID string, callback handlers.Callback) error {
	if requestID == "" {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "'id' field is required and cannot be empty. Use a new unique request 'id' for each request", callback)
		return errors.New("empty request ID")
	}
	// Request IDs from users must not contain "/", since this character is reserved
	// for internal node-to-node message routing (e.g., "http_action/{workflowID}/{uuid}").
	if strings.Contains(requestID, "/") {
		h.handleUserError(ctx, requestID, jsonrpc.ErrInvalidRequest, "request ID must not contain '/'", callback)
		return errors.New("request ID must not contain '/'")
	}
	return nil
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
