## Title
Global, workflow-unscoped `requestID` collision in HTTP Trigger Handler allows unprivileged callers to DoS other users' trigger requests - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The underlying bug class from the report is a shared "nonce"/uniqueness value (`block.number`) that is not scoped to the entity performing the operation (the pool), allowing any unprivileged actor to pre-occupy that value and cause a legitimate operation to be rejected. The `httpTriggerHandler` in the Gateway's HTTP-trigger capability has the same structural flaw: request uniqueness is enforced on a single global map keyed only by the caller-supplied `requestID` string, with no scoping to workflow, owner, or DON/shard. Any unprivileged client can pre-claim a `requestID` value and cause a different, unrelated caller's legitimate request using the same ID to be rejected.

### Finding Description
`httpTriggerHandler` stores in-flight requests in a single node-wide map: [1](#0-0) 

`setupCallback` enforces uniqueness purely against this global map, keyed only by the client-supplied `requestID` (`req.ID`), with no namespacing by `workflowID`, workflow owner, or DON/shard: [2](#0-1) 

The only validation applied to `requestID` is that it is non-empty and doesn't contain `/`: [3](#0-2) 

This is exactly analogous to the reported bug: a value meant to guarantee per-operation uniqueness (`block.number` for a pool's rebalance order vs. `requestID` for a user's trigger call) is drawn from a single, node-wide namespace shared across all unrelated callers/workflows instead of being scoped per-tenant (per pool vs. per workflow/owner). Because the namespace is shared, any unprivileged, unauthenticated-at-this-stage caller (authentication happens per-workflow later, but the `requestID` collision check happens for any syntactically valid request reaching the handler) can occupy a `requestID` value ahead of a legitimate caller. The legitimate caller's subsequent request with the same `requestID` is rejected outright with `jsonrpc.ErrConflict` before it is ever dispatched to the DON: [4](#0-3) 

Node responses are also routed back purely by `resp.ID` against this same global map, reinforcing that the ID is the sole disambiguator across the entire handler instance, not per caller: [5](#0-4) 

### Impact Explanation
Any unprivileged remote caller who can guess or predict a `requestID` that another legitimate workflow owner will use (e.g., sequential IDs, timestamps, or other predictable client-side ID schemes commonly used for idempotency keys) can send a request against any registered workflow using that ID first. This causes the legitimate caller's genuine request with the same `requestID` to be rejected with a conflict error and never delivered to the DON, denying that specific invocation of the victim's workflow trigger — a denial-of-service on a target's HTTP-triggered workflow execution, without requiring any credentials tied to the victim's workflow.

### Likelihood Explanation
The requestID namespace is enforced only by a simple presence/format check (non-empty, no `/`), with no per-tenant scoping, so exploitation requires no special privileges — only the ability to send a well-formed `workflows.execute` JSON-RPC request to the gateway with a chosen `id`. Success depends on the attacker being able to predict/guess a `requestID` value the victim's client will use next, which is plausible for common client patterns (incrementing counters, timestamps, or low-entropy identifiers), making this a moderate-likelihood, low-cost griefing vector.

### Recommendation
Scope the in-flight-request uniqueness check (and the `callbacks` map key) to a composite of `workflowID` (or workflow owner) and `requestID` rather than `requestID` alone, so that request ID collisions can only occur within the same workflow/owner's own request stream, not across unrelated callers.

### Proof of Concept
1. Attacker registers/owns Workflow A (or simply submits any syntactically-valid `workflows.execute` request targeting any workflow they can address) and sends a trigger request with `id = "1001"`.
2. `setupCallback` inserts `h.callbacks["1001"]` into the shared, node-wide map (see `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:419-426`).
3. Victim's client (using a predictable/incrementing `id` scheme) concurrently sends its own legitimate `workflows.execute` request for Workflow B with the same `id = "1001"`.
4. Victim's request hits the same `found` check in `setupCallback`, returns `jsonrpc.ErrConflict` ("requestID: 1001 has already been used..."), and is never forwarded to the DON — the victim's workflow execution for that request is denied, purely because of an ID collision engineered by an unrelated, unprivileged attacker.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-147)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L474-497)
```go
func (h *httpTriggerHandler) HandleNodeTriggerResponse(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	h.lggr.Debugw("handling trigger response", "requestID", resp.ID, "nodeAddr", nodeAddr, "error", resp.Error, "result", resp.Result)
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	saved, exists := h.callbacks[resp.ID]
	if !exists {
		return errors.New("callback not found for request ID: " + resp.ID)
	}
	if saved.processed {
		h.lggr.Debugw("request already processed, ignoring late response", "requestID", resp.ID, "nodeAddr", nodeAddr)
		return nil
	}

	// Route the response into the aggregator for the shard that owns this node.
	shard, ok := h.nodeAddrToShard[nodeAddr]
	if !ok {
		return fmt.Errorf("received trigger response from unknown node %s (no owning shard)", nodeAddr)
	}
	agg, ok := saved.responseAggregators[shard.donID]
	if !ok {
		// The node belongs to a shard this workflow isn't assigned to (or the
		// callback was captured before the workflow was assigned there).
		return fmt.Errorf("node %s (shard %s) is not assigned to workflow for request ID %s", nodeAddr, shard.donID, resp.ID)
	}
```
