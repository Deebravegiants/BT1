## Finding

### Title
Gateway HTTP trigger callback map keyed globally by user-supplied `requestID` allows any authenticated caller to block/DoS other users' requests (key-collision/trolling) - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The gateway's HTTP trigger handler stores in-flight request state in a single map keyed only by the client-supplied JSON-RPC `id` (`requestID`), with no scoping to the calling workflow or owner. Any user who can authenticate to *any* workflow can reserve an arbitrary `requestID` string, causing every other user's (unrelated workflow's) request that happens to use the same `requestID` value to be rejected outright.

### Finding Description
`httpTriggerHandler.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback`, keyed purely by the string `requestID` taken directly from the incoming JSON-RPC request `id` field: [1](#0-0) 

`validateRequestID` only rejects empty IDs or ones containing `/`; any other string, including short, predictable, or commonly-used IDs, is accepted: [2](#0-1) 

`setupCallback` checks for prior occupancy of that global key and rejects the request with `jsonrpc.ErrConflict` if any *other* in-flight (or not-yet-reaped) request already holds it — regardless of which workflow or owner created the earlier entry: [3](#0-2) 

Critically, `authorizeRequest`/`workflowMetadataHandler.Authorize` only validates that the caller is authorized for the *workflow they specified* — it does not, and cannot, prevent that caller from choosing a `requestID` value that a completely unrelated workflow's legitimate caller is also likely to use: [4](#0-3) 

Because the key space (`requestID`) is entirely global and chosen by the client, and reservations persist until the periodic reaper runs (bounded by `CleanUpPeriodMs`), any authenticated-but-unprivileged caller for Workflow A can pre-claim a `requestID` that a caller for unrelated Workflow B is expected to use (e.g., predictable/sequential IDs, or values observed from public logs/telemetry), denying Workflow B's legitimate request: [5](#0-4) 

This is the same bug class as the referenced Osmosis fix: incentive records were keyed by a shared/global identifier rather than scoped per owner, letting any unprivileged address claim/collide with another owner's key to grief or DoS them. Here the shared identifier is `requestID`, and the fix pattern (scoping the key to the resource owner — i.e., `(workflowID, requestID)` or `(owner, requestID)` instead of bare `requestID`) directly applies.

### Impact Explanation
Any client that can obtain valid trigger auth for at least one workflow (even their own, otherwise-benign workflow) can deny service to arbitrary other workflows/users by repeatedly claiming `requestID` values before the legitimate caller does, or immediately after guessing/observing them, causing `handleUserTriggerRequest` to reject those legitimate calls with "requestID ... has already been used." This is a availability/DoS impact on the gateway's HTTP trigger path affecting unrelated, unprivileged victim workflows.

### Likelihood Explanation
Exploitability requires only ordinary, unprivileged access to the gateway's HTTP trigger endpoint with valid auth for some workflow (attacker's own). No special role or privilege escalation is needed to reach `setupCallback`; the collision surface is any string not containing `/`, making guessable/predictable request IDs (sequential counters, UUID-v1 style, timestamps, or simply well-known test IDs) practical griefing targets.

### Recommendation
Scope the `callbacks` map key to include the workflow (and ideally owner) alongside the client-supplied `requestID`, e.g. `key = workflowID + "/" + requestID` (mirroring the existing internal reservation for `/` as a separator), so that request-ID collisions can only occur within the same workflow's own request stream, not across unrelated workflows/owners. Apply the same scoping to `HandleNodeTriggerResponse` lookups and to the reaper.

### Proof of Concept
1. Attacker holds valid JWT/auth for Workflow A (their own).
2. Attacker sends `workflows.execute` request to the gateway's HTTP trigger endpoint with `id = "victim-123"` for Workflow A. `setupCallback` inserts `callbacks["victim-123"]`.
3. Legitimate user of unrelated Workflow B sends their own request using the same client-chosen `id = "victim-123"` (e.g., because their client library generates deterministic/sequential IDs, or the attacker observed the value elsewhere).
4. `setupCallback` finds `h.callbacks["victim-123"]` already present and rejects Workflow B's legitimate request with `jsonrpc.ErrConflict`, even though it originated from a completely different, unrelated workflow/owner: [6](#0-5)

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
