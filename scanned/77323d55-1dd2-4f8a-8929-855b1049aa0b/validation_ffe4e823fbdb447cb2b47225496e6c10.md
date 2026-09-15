### Title
`HTTPTriggerHandler` request-ID namespace is shared across all callers/workflows, allowing front-run DoS of another user's trigger request - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The gateway's HTTP trigger handler deduplicates in-flight requests using a single global map keyed only by the client-supplied JSON-RPC `id` (`requestID`). This key is not scoped to the caller, the workflow, or the workflow owner. Any authenticated workflow caller can pick an arbitrary `id` string and, by submitting it first, occupy that slot in the shared map, causing any other legitimate request that later arrives with the same `id` (targeting a different, unrelated workflow) to be rejected outright — the exact "orderId collision without sender binding" bug class from the report, applied to the gateway's request-tracking namespace instead of an orderId.

### Finding Description
`HandleUserTriggerRequest` processes requests in this order: `validatedTriggerRequest` (format-only ID validation), `resolveWorkflowID`, `authorizeRequest` (validates the caller's JWT/key against the specific `workflowID` in the request), `checkRateLimit`, and finally `setupCallback`, which performs the actual uniqueness check: [1](#0-0) 

```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
	...
	h.callbacks[requestID] = savedCallback{...}
```

`h.callbacks` is declared as `map[string]savedCallback // requestID -> savedCallback` [2](#0-1) , a single map shared across every workflow and every caller served by this handler instance. The only per-request uniqueness constraint enforced anywhere is this global key collision check; there is no additional binding of the map key to `workflowID`, `workflowOwner`, or the caller's authorized key. `validateRequestID` only checks that the ID is non-empty and does not contain `/` — it does not enforce caller-specific scoping either [3](#0-2) .

Because `authorizeRequest` only validates that the caller is authorized for *their own* `workflowID` [4](#0-3) , any caller who holds a valid authorized key for *any* workflow can submit a request whose `id` matches (or is guessed/predicted to match) a victim's upcoming request `id`, for a completely different workflow they are not otherwise related to. If the attacker's request reaches `setupCallback` first, the victim's later request with the same `id` is rejected with `ErrConflict` — denial of service of a specific request without needing any privilege over the victim's workflow.

This mirrors the reported Dinari `OrderProcessor.requestOrder` issue: a resource-uniqueness key (`orderId` there, `requestID`/map key here) is derived only from attacker-influenceable/collidable input and is not bound to the identity of the legitimate requester, so an unrelated unprivileged actor can occupy the slot first and block the legitimate operation.

### Impact Explanation
An attacker with legitimate (but unrelated) authorization to trigger any workflow on the gateway can selectively deny service to a specific victim request by pre-occupying its `requestID` slot in the shared map, causing the victim's request to be rejected with `ErrConflict` ("has already been used") instead of being processed. This is a targeted request-level DoS on the internet-facing HTTP trigger gateway path, degrading availability/reliability guarantees for the affected caller without requiring any access to the victim's workflow, keys, or credentials.

### Likelihood Explanation
Exploitability requires the attacker to hold a valid authorized key for at least one workflow on the gateway (a low bar, since workflow triggering is designed to be accessible to authorized external callers) and to be able to predict or race the victim's `id` value. If victim clients use predictable, sequential, or otherwise guessable IDs (or the attacker can observe/replay an ID from a prior interaction), the race is straightforward; even against random IDs, this remains a real availability risk whenever ID choice isn't strictly random/high-entropy on the client side, which the handler does not enforce or require.

### Recommendation
Scope the request-dedup map key to include an identity component the attacker cannot forge, e.g. key by `(workflowOwner, workflowID, requestID)` or `(authorizedKey, requestID)` rather than by `requestID` alone, mirroring the fix recommended in the source report (binding the uniqueness key to the legitimate requester's identity, e.g. `msg.sender` in the on-chain analog). This should be enforced in `setupCallback` (and any code paths, such as `sendWithRetries`'s error path, that also look up `h.callbacks` by bare `requestID`) so that two unrelated workflows/owners can never collide on the same map slot.

### Proof of Concept
1. Attacker obtains a valid authorized key for `workflowA` (any workflow they're permitted to trigger).
2. Attacker predicts/observes that a victim will soon send a trigger request for `workflowB` with `id = "X"`.
3. Attacker sends `{"method":"workflows.execute","id":"X","params":{"workflow":{"workflowID":"workflowA",...}}}` — this passes `authorizeRequest` (valid for `workflowA`) and reaches `setupCallback`, inserting `h.callbacks["X"]`.
4. Victim's legitimate request `{"id":"X","params":{"workflow":{"workflowID":"workflowB",...}}}` arrives afterward; `setupCallback` finds `h.callbacks["X"]` already present and returns `jsonrpc.ErrConflict` with message `"requestID: X has already been used..."`, denying the victim's request entirely [5](#0-4) .

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
