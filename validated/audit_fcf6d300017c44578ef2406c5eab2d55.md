### Title
Cross-workflow request-ID squatting causes denial of service in the CRE Gateway HTTP Trigger Handler - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The Gateway's HTTP Trigger Handler (`httpTriggerHandler`) tracks in-flight user trigger requests in a single map keyed **only by the client-supplied `requestID`**, with no per-workflow namespacing. Any authorized workflow owner can "reserve" an arbitrary `requestID` by submitting a trigger request, and that ID is then unavailable to *any other workflow* on the same gateway node until the request completes or is reaped after a fixed timeout (default 10 minutes). This is directly analogous to the bonding-mechanism DOS in the external report: a cheap, low-barrier action locks a shared resource slot and blocks unrelated legitimate users until an automatic expiry fires.

### Finding Description
`httpTriggerHandler.callbacks` is declared as a single global map: [1](#0-0) 

`setupCallback` enforces uniqueness of `requestID` across the **entire handler instance**, not scoped to the requesting workflow: [2](#0-1) 

The only validation performed on the client-supplied `requestID` is that it is non-empty and does not contain `/`: [3](#0-2) 

Because `HandleUserTriggerRequest` resolves and authorizes the workflow *before* calling `setupCallback`, but never mixes `workflowID` into the callback map key, a first request wins the ID for the entire gateway instance: [4](#0-3) 

The occupied slot is only released when the original request completes (`markCallbackProcessed`/`cleanupCallback`) or via the periodic reaper, which runs on `CleanUpPeriodMs` (default 10 minutes): [5](#0-4) [6](#0-5) 

Rate limiting is applied per workflow owner (`checkRateLimit`), not globally, so an attacker controlling even a single authorized workflow can submit a steady stream of requests (bounded only by their own per-workflow rate limit, default burst 50 / 5 rps) each using a different guessed or brute-forced `requestID`, occupying that key for up to 10 minutes and denying any other workflow's legitimate request using the same ID (rejected immediately with `jsonrpc.ErrConflict`, "in-flight request ID"): [7](#0-6) 

This is the same bug class as the external report: a cheap, unprivileged action (bonding an auction / squatting a request ID) creates a lock on a shared resource that only clears after a fixed timeout, with no way for the victim to pre-empt or cancel it.

### Impact Explanation
An attacker who controls (or cheaply registers) any workflow authorized against the gateway can deny service to unrelated workflows' HTTP-trigger executions by squatting on their `requestID`s, since the in-flight map is shared across all workflows served by the same gateway/DON shard set rather than being scoped per workflow. Legitimate executions using a colliding ID are rejected outright with `ErrConflict` and never reach the DON. This can disrupt time-sensitive CRE workflow executions triggered via HTTP for up to the reaper interval (10 minutes by default), which is a meaningful availability impact for a production automation platform.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or brute-force a victim's `requestID` values, since IDs are client-chosen strings with only a "no `/`" restriction and no per-workflow scoping requirement. Many integrations use predictable ID schemes (timestamps, counters, deterministic hashes), making collision plausible; even without prediction, an attacker with a registered workflow and default rate limits can occupy thousands of IDs within a 10-minute reaping window. The barrier to entry is low (own an authorized workflow) compared to the original bonding-auction case, and no economic penalty (analogous to a burned bond) exists to disincentivize repeated abuse.

### Recommendation
Scope the in-flight callback map key by `(workflowID, requestID)` instead of `requestID` alone, so that one workflow cannot occupy or interfere with another workflow's request-ID namespace. Additionally, consider capping the number of concurrently in-flight callbacks a single workflow/owner may hold, and reducing `CleanUpPeriodMs` for unacknowledged, unauthenticated-collision cases, to shrink the DOS window.

### Proof of Concept
1. Attacker registers/owns Workflow A (any workflow with a valid signing key can be authorized per `WorkflowMetadataHandler.Authorize`).
2. Attacker submits `MethodWorkflowExecute` trigger requests to the gateway with `id = "X"` repeatedly for many candidate values of `X` (guessed/brute-forced), each properly signed for Workflow A. Each call succeeds and calls `setupCallback`, inserting `h.callbacks["X"]`.
3. Victim's Workflow B later submits a legitimate trigger request that happens to use `id = "X"`. `setupCallback` finds `h.callbacks["X"]` already present (from Workflow A) and immediately returns `jsonrpc.ErrConflict` via `handleUserError`, denying Workflow B's execution.
4. Workflow B's request will continue to fail for any request using the colliding ID until Workflow A's request is processed or reaped (up to `defaultCleanUpPeriodMs` = 10 minutes), at which point Attacker can repeat with a new batch of IDs.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L64-65)
```go
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-146)
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

	strippedWorkflowID := strings.TrimPrefix(workflowID, "0x")
	legacyExecutionID, err := workflows.EncodeExecutionID(strippedWorkflowID, req.ID) //nolint:staticcheck // legacy ID kept for observability comparison
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID: " + err.Error())
	}
	// Workflows shouldn't use more than one HTTP trigger. If we ever need to support multiple triggers, we'd need to pass
	// trigger index to the Gateway handler and somehow allow senders to pick. For now, we use trigger index 0.
	// Execution IDs here are used only for logging.
	executionIDWithTriggerIndex, err := workflows.GenerateExecutionIDWithTriggerIndex(strippedWorkflowID, req.ID, 0)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error generating execution ID with trigger index: " + err.Error())
	}
	h.lggr.Debugw("processing request",
		"legacyExecutionID", legacyExecutionID,
		"executionIDWithTriggerIndex", executionIDWithTriggerIndex,
		"requestID", req.ID,
		"workflowID", workflowID)

	reqWithKey, err := reqWithAuthorizedKey(triggerReq, *key)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInternal, internalErrorMessage, callback)
		return errors.New("error marshaling trigger request: " + err.Error())
	}

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L392-416)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L29-43)
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
```
