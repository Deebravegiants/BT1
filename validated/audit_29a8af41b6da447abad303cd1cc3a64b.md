Audit Report

## Title
`HTTPTriggerHandler` deduplicates in-flight requests using a global `requestID`-only map, allowing an authorized caller for one workflow to front-run and deny a request for an unrelated workflow - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

## Summary
`httpTriggerHandler.setupCallback` uses `h.callbacks map[string]savedCallback` keyed solely by the client-supplied JSON-RPC `id`, with no binding to `workflowID`, `workflowOwner`, or the caller's authorized key. Any caller holding a valid authorized key for *any* workflow can occupy an arbitrary `id` slot first, and a legitimate request for a *different* workflow arriving later with the same `id` is rejected with `jsonrpc.ErrConflict`, denying that specific request.

## Finding Description
`HandleUserTriggerRequest` validates format-only ID uniqueness constraints (`validateRequestID`, non-empty and no `/`) at [1](#0-0) , then authorizes the caller only against their own target `workflowID` via `authorizeRequest`/`WorkflowMetadataHandler.Authorize` at [2](#0-1) . Neither step ties the `id` to the caller's identity or workflow. The actual uniqueness/dedup check happens in `setupCallback`, which looks up and inserts into the single global map keyed by bare `requestID`: [3](#0-2)  and [4](#0-3) . The map field itself is declared without any composite key: [5](#0-4) . This confirms the reported mechanism exactly: the collision check is global across all workflows/callers, and any caller authorized for workflow A can occupy the `id` slot for a request that a different caller intends to send for workflow B, causing the victim's later, otherwise-valid request to fail with "requestID: X has already been used."

## Impact Explanation
This is a genuine, code-confirmed availability issue on the gateway's HTTP trigger path: an authorized-but-unrelated caller can selectively deny a specific in-flight request belonging to another workflow/owner by winning a race on a shared, unscoped map key. It does not grant privilege escalation, key/secret exposure, fund movement, or response corruption — it is a per-request denial-of-service limited to the specific colliding `id`. This maps to a DoS/reliability degradation on an internet-facing gateway path rather than a data-integrity or authentication bypass; the requestor still needs a legitimate authorized key for at least one workflow, and the "success" of the attack is entirely conditioned on winning a race against unpredictable client-chosen IDs.

## Likelihood Explanation
Exploitability requires: (1) the attacker holds a valid authorized key for some workflow on the gateway, and (2) the attacker can predict or observe the victim's `id` value ahead of time and win a race to submit it first. In practice, request `id`s are typically high-entropy client-generated values (e.g., UUIDs) not observable by other unrelated callers before submission, making prediction impractical for a random ID. The report does not demonstrate any means by which an attacker learns a victim's future `id`. As `id` values are not attacker/broker-controlled or exchanged via any accessible channel described here, the realistic likelihood of hitting a specific victim's `id` is low, though the underlying missing-scoping root cause is real and could compound with any other bug that makes an ID predictable or reused (e.g., a client-side sequential-ID bug).

## Recommendation
Scope the deduplication key beyond the bare `requestID`, e.g. key `h.callbacks` by `(workflowID, requestID)` or `(authorizedKey, requestID)`, in both `setupCallback` and the `sendWithRetries` error-path lookup (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` L651-656), and in `HandleNodeTriggerResponse`'s lookup by `resp.ID` (L478) and `cleanupCallback` (L463-472), so that requests for different workflows/owners can never collide on the same map slot, regardless of caller-supplied `id`.

## Proof of Concept
1. Attacker holds a valid authorized key for `workflowA`.
2. Attacker learns/guesses that a victim will submit `id = "X"` for `workflowB` (this step is not demonstrated as feasible against high-entropy client IDs, but assume it for PoC purposes).
3. Attacker sends `{"method":"workflows.execute","id":"X","params":{"workflow":{"workflowID":"workflowA",...}},"auth":<validForWorkflowA>}`; this passes `authorizeRequest` and reaches `setupCallback`, inserting `h.callbacks["X"]`.
4. Victim's request `{"id":"X","params":{"workflow":{"workflowID":"workflowB",...}}}` arrives; `setupCallback` finds `h.callbacks["X"]` occupied and returns `ErrConflict`, denying the victim's request — reproducible as a Go unit test directly against `httpTriggerHandler.setupCallback` by calling it twice with the same `requestID` but different `workflowID`s.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L58-72)
```go
type httpTriggerHandler struct {
	services.StateMachine
	config                  ServiceConfig
	shards                  []*shardEndpoint
	nodeAddrToShard         map[string]*shardEndpoint
	lggr                    logger.Logger
	callbacksMu             sync.Mutex
	callbacks               map[string]savedCallback // requestID -> savedCallback
	stopCh                  services.StopChan
	workflowMetadataHandler *WorkflowMetadataHandler
	userRateLimiter         limits.RateLimiter
	metrics                 *metrics.Metrics
	wg                      sync.WaitGroup
	orgResolver             orgresolver.OrgResolver // optional; nil if the node isn't configured to resolve orgs (e.g. no Linking Service)
}
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L447-455)
```go
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
