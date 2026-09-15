Audit Report

## Title
Gateway HTTP trigger callback map is keyed globally by client-supplied `requestID`, allowing any authenticated caller to DoS unrelated workflows via requestID collision - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

## Summary
`httpTriggerHandler.callbacks` is a single map keyed only by the JSON-RPC `id` string supplied by the client, with no scoping to workflow or owner. Because `setupCallback` rejects any request whose `requestID` already exists in this global map — regardless of which workflow originally reserved it — a caller authorized for any workflow can pre-claim a `requestID` value and cause `workflows.execute` requests from a completely unrelated workflow using the same ID to be rejected with `jsonrpc.ErrConflict`.

## Finding Description
The map declaration and comment confirm the key is purely `requestID`, with no workflow/owner component: [1](#0-0) 

`validateRequestID` only forbids empty strings and strings containing `/`; any other value, including predictable or short strings, is accepted as a valid ID for any workflow: [2](#0-1) 

`authorizeRequest` calls `workflowMetadataHandler.Authorize(workflowID, req.Auth, req)`, which validates the caller's authorization against the specific `workflowID` in their own request — it has no visibility into, and cannot prevent, that caller choosing a `requestID` that a different, unrelated workflow's caller might also use: [3](#0-2) 

`setupCallback` then performs the actual reservation, keyed globally by `requestID` alone, and rejects the request outright if any other entry — from any workflow — already occupies that key: [4](#0-3) 

The entry persists in the map until either the request completes/is processed, or the periodic reaper (`reapExpiredCallbacks`, run every `CleanUpPeriodMs`) removes it: [5](#0-4) 

No other code path scopes or namespaces this key by workflow, owner, or org — `HandleNodeTriggerResponse` also looks up `h.callbacks[resp.ID]` using the same global keyspace. [6](#0-5)  This confirms the root cause: the collision-detection/reservation mechanism conflates "uniqueness within one workflow's request stream" (the intended semantics per the user-facing error message "Ensure the requestID is unique for each request") with "uniqueness across the entire gateway," which is a broken security/isolation assumption between unrelated tenants/workflows.

## Impact Explanation
This is a genuine cross-workflow availability/DoS bug: a caller holding valid trigger auth for Workflow A (which could be their own, otherwise legitimate workflow) can occupy `requestID` values in the shared map, causing `workflows.execute` requests for an unrelated Workflow B that happen to reuse the same client-generated ID to be rejected with `ErrConflict`, denying service to that unrelated workflow's legitimate caller. This maps to an in-scope availability/DoS impact on the gateway's HTTP trigger path.

## Likelihood Explanation
Exploitation requires only valid, unprivileged trigger authorization for any single workflow — no elevated role, admin access, or privilege escalation is needed to reach `setupCallback`. The attack surface for collision is broad (any string without `/`), making guessable or predictable request IDs (sequential counters, timestamps, common test values) practical, low-cost griefing vectors that are repeatable at will and bounded only by the reaper interval.

## Recommendation
Scope the `callbacks` map key to include the workflow (and ideally the resolved owner) alongside the client-supplied `requestID`, e.g. `workflowID + "/" + requestID`, mirroring the existing internal `/`-based reservation scheme used for node-to-node routing. Apply the same scoping consistently to `setupCallback`, `HandleNodeTriggerResponse`, `cleanupCallback`, and `reapExpiredCallbacks` so that ID collisions can only occur within a single workflow's own request stream.

## Proof of Concept
1. Obtain valid trigger auth for Workflow A (attacker-controlled, unprivileged).
2. Send a `workflows.execute` JSON-RPC request to the gateway HTTP trigger endpoint with `id = "victim-123"` targeting Workflow A; `setupCallback` inserts `callbacks["victim-123"]`.
3. Before that entry is reaped/cleaned up, send (or have a legitimate caller send) a `workflows.execute` request for unrelated Workflow B using the same `id = "victim-123"`.
4. Observe that `setupCallback` finds the existing entry and rejects Workflow B's request with `jsonrpc.ErrConflict` ("requestID: victim-123 has already been used..."), confirmed by [7](#0-6) , demonstrating cross-workflow denial of service via global requestID keying.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L64-65)
```go
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L474-481)
```go
func (h *httpTriggerHandler) HandleNodeTriggerResponse(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	h.lggr.Debugw("handling trigger response", "requestID", resp.ID, "nodeAddr", nodeAddr, "error", resp.Error, "result", resp.Result)
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	saved, exists := h.callbacks[resp.ID]
	if !exists {
		return errors.New("callback not found for request ID: " + resp.ID)
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
