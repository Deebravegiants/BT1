Audit Report

## Title
Gateway HTTP trigger callback map keyed globally by user-supplied `requestID` allows cross-workflow key collisions and DoS - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

## Summary
`httpTriggerHandler.callbacks` is a single map keyed only by the client-supplied JSON-RPC `id` (`requestID`), with no scoping to workflow or owner, as declared and used in `setupCallback`. Because `validateRequestID` only rejects empty IDs or ones containing `/`, and `authorizeRequest` only validates the caller's authorization for the workflow they specified (not global uniqueness of the ID across workflows), any authenticated caller with valid credentials for *some* workflow can pre-claim a `requestID` value, causing an unrelated workflow's legitimate request using that same value to be rejected with `jsonrpc.ErrConflict`.

## Finding Description
The root cause is confirmed in code: the map is declared as `map[string]savedCallback // requestID -> savedCallback` [1](#0-0) , and `setupCallback` checks and inserts into this map using only the bare `requestID`, even though `workflowID` is passed into the function (it is only used afterward for shard/aggregator assignment, never as part of the map key) [2](#0-1) .

`validateRequestID` performs only minimal validation — non-empty and no `/` character — and does not enforce any per-workflow or per-owner scoping [3](#0-2) .

`authorizeRequest` calls `h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)`, which validates that the caller is authorized *for the workflow they named* — it has no visibility into, and cannot prevent, collisions with `requestID` values chosen by callers of entirely different workflows [4](#0-3) . The call flow in `HandleUserTriggerRequest` confirms `setupCallback` is invoked using the raw `req.ID` after authorization/rate-limiting, with `workflowID` only informing shard assignment, not key scoping [5](#0-4) .

The reaper iterates and cleans up the same global map on a timer (`CleanUpPeriodMs`), meaning a maliciously reserved key persists and blocks collisions until it expires [6](#0-5) .

This matches the claim precisely: the key space for in-flight request tracking is entirely global and client-controlled, with no workflow/owner scoping, despite `workflowID` being readily available at the point of map insertion.

## Impact Explanation
This is a legitimate availability/DoS finding: an authenticated caller with valid credentials for their own (potentially unrelated) workflow can select a `requestID` also likely to be used by a legitimate caller of a different, unrelated workflow, causing that legitimate request to be rejected with "requestID ... has already been used." This is a concrete, code-confirmed cross-user interference / DoS on the gateway's HTTP trigger request path, falling under the "cross-user response corruption" impact class in scope for the gateway.

## Likelihood Explanation
Exploitability requires only valid authorization for at least one workflow (which could be the attacker's own, legitimately obtained credentials) — no elevated privilege or bypass of the workflow-specific `Authorize` check is needed to reach `setupCallback`. The collision surface (any string without `/`) makes this practical against predictable/sequential/timestamp-based or well-known `requestID` schemes used by client libraries. The finding is fully reproducible by reading the code path and requires no speculative assumptions.

## Recommendation
Scope the `callbacks` map key to include the workflow ID (and ideally the authorized owner/key) alongside the client-supplied `requestID`, e.g., `key = workflowID + "/" + requestID`, consistent with the existing internal convention of using `/` as a separator for node-to-node routing. Apply the same scoping consistently to any lookup/cleanup path that references `h.callbacks` by `requestID` alone (e.g., the reaper in `reapExpiredCallbacks`, and any node-response correlation logic), and consider deriving the key from the already-computed `legacyExecutionID`/`executionIDWithTriggerIndex` (which already combine `workflowID` and `requestID`) rather than the bare `requestID`.

## Proof of Concept
1. Attacker obtains valid authorization for Workflow A (their own, legitimately controlled workflow).
2. Attacker sends a `workflows.execute` JSON-RPC request to the gateway's HTTP trigger endpoint with `id = "victim-123"` targeting Workflow A. `setupCallback` inserts `h.callbacks["victim-123"]`.
3. Before the reaper clears this entry (bounded by `CleanUpPeriodMs`), a legitimate user of unrelated Workflow B sends a request with the same client-generated `id = "victim-123"` (e.g., due to deterministic/sequential ID generation in their client, or because the value was observed/guessed).
4. `setupCallback` finds `h.callbacks["victim-123"]` already occupied and rejects Workflow B's legitimate request with `jsonrpc.ErrConflict` ("requestID: victim-123 has already been used..."), confirming denial of service against an unrelated workflow's legitimate request [7](#0-6) .

This can be directly validated with a Go unit test on `httpTriggerHandler.HandleUserTriggerRequest`/`setupCallback` by authorizing two distinct workflows and submitting requests with the same `req.ID` for each, observing that the second is rejected regardless of workflow identity.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L368-376)
```go
func (h *httpTriggerHandler) authorizeRequest(ctx context.Context, workflowID string, req *jsonrpc.Request[json.RawMessage], callback handlers.Callback) (*gateway_common.AuthorizedKey, error) {
	h.lggr.Debugw("authorizing request", "workflowID", workflowID, "requestID", req.ID)
	key, err := h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)
	if err != nil {
		h.handleUserError(ctx, req.ID, jsonrpc.ErrInvalidRequest, "Auth failure: "+err.Error(), callback)
		return nil, errors.Join(errors.New("auth failure"), err)
	}
	return key, nil
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
