## Finding [1](#0-0) 

### Title
Cross-workflow HTTP trigger request-ID collision enables unprivileged DoS of other workflows' legitimate requests - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Gateway's HTTP Trigger Handler tracks in-flight user requests in a single, gateway-wide map keyed only by the caller-supplied `req.ID` string, with no namespacing by workflow ID or workflow owner. Any authenticated caller of the internet-facing trigger endpoint (authorized only for their *own* workflow) can pick a `requestID` that collides with a concurrent request from a completely different workflow/owner, causing the victim's legitimate request to be rejected.

### Finding Description
`HandleUserTriggerRequest` validates the trigger request, resolves the workflow, authorizes the caller against that specific workflow, checks the per-workflow-owner rate limit, and then calls `setupCallback`: [2](#0-1) 

`setupCallback` guards uniqueness of `requestID` purely against the shared `h.callbacks` map:

```go
if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, ...)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
```

This map is declared without any per-owner or per-workflow scoping — `callbacks map[string]savedCallback // requestID -> savedCallback` — and `validateRequestID` only rejects empty IDs or IDs containing `/`, doing nothing to prevent one tenant's chosen ID from colliding with another tenant's ID: [3](#0-2) 

Because `req.ID` is fully attacker-controlled and authorization (`authorizeRequest`) only checks that the caller can invoke *their own* workflow (not that they own the `requestID` namespace), any workflow owner authorized for at least one workflow can send a flood of trigger requests using IDs likely to be chosen by other tenants (sequential integers, UUIDs harvested from other public interactions, etc.), reserving those IDs in the shared map before the legitimate owner's request arrives. The legitimate request is then rejected with `jsonrpc.ErrConflict` ("requestID has already been used"), even though it targets a completely different, unrelated workflow. This mirrors the reported zkEVM bug class: a low-privilege actor manipulates a check that is supposed to gate resource usage per-entity, but the check is actually keyed globally, letting the actor "pre-mark" an identifier and deny service to a legitimate, unrelated party.

The rate limiter that could otherwise bound this abuse is scoped per-workflow-owner via `contexts.WithCRE(ctx, contexts.CRE{Owner: ...})`, so it does not protect against an attacker abusing their *own* rate-limited quota to poison the *global* `callbacks` keyspace shared by all tenants: [4](#0-3) 

### Impact Explanation
An authorized-for-only-their-own-workflow, otherwise unprivileged caller can deny service to unrelated workflows/owners on the same Gateway/DON by colliding on `requestID` values, causing legitimate HTTP-triggered workflow executions to fail with `ErrConflict` until the reaper interval (`CleanUpPeriodMs`) expires the stale entry. This is a persistent, repeatable DoS vector against arbitrary third-party workflows reachable over the internet-facing Gateway HTTP trigger surface, without requiring any privilege beyond having one authorized workflow of one's own.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or guess the `requestID` values chosen by victim callers (e.g., low-entropy/sequential IDs, or IDs learned via other channels). Where IDs are high-entropy random UUIDs chosen by careful clients, collision is unlikely; however, nothing in the code prevents an attacker from proactively reserving many candidate IDs, and no scoping exists to eliminate this class of collision entirely, so likelihood scales with how predictable client-chosen IDs are in practice.

### Recommendation
Scope the in-flight `callbacks` map key by `(workflowID, requestID)` or `(workflowOwner, requestID)` instead of `requestID` alone, so that request-ID reservations from one workflow/owner cannot collide with or block requests belonging to a different workflow/owner.

### Proof of Concept
1. Attacker obtains authorization for their own workflow `W_attacker` (a normal, unprivileged onboarding step).
2. Attacker sends a flood of `workflows.execute` trigger requests to the Gateway using `req.ID` values equal to common/sequential/guessable IDs (e.g., `"1"`, `"2"`, UUID patterns observed from a victim's client), targeting `W_attacker` so authorization succeeds and `setupCallback` reserves the ID in the shared `h.callbacks` map.
3. Before the victim owner's legitimate request for a different workflow `W_victim` using the same `req.ID` arrives, `setupCallback` for the victim finds `h.callbacks[requestID]` already present and returns `jsonrpc.ErrConflict`, denying the victim's legitimate execution request despite no relationship between the attacker's and victim's workflows.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L63-66)
```go
	lggr                    logger.Logger
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
	stopCh                  services.StopChan
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
