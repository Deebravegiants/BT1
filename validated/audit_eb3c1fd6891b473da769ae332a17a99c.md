## Analysis Result

### Title
Global, unscoped `requestID` namespace in the Gateway HTTP Trigger Handler lets any authorized caller squat another workflow's request ID and block its execution - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

### Summary
The external report describes a class of bug where a shared, globally-writable registration namespace (the `Registry.register` function) lets an unprivileged caller pre-register an identifier that a legitimate actor will later need, causing the legitimate registration to revert. The `httpTriggerHandler` in the Chainlink Gateway's HTTP trigger path has the same structural flaw: pending requests are tracked in a single process-wide map keyed **only** by the client-supplied `requestID`, with no per-workflow or per-owner scoping, so any caller who can get one of their own workflow requests authorized can occupy another workflow's `requestID` and force that request to be rejected.

### Finding Description
`httpTriggerHandler.callbacks` is declared as a single global map keyed by `requestID` alone: [1](#0-0) 

`HandleUserTriggerRequest` validates the request, resolves the **caller's own** `workflowID`, authorizes the caller against that workflow, checks the caller's own rate limit, and only then calls `setupCallback`: [2](#0-1) 

`setupCallback` performs the actual "registration" check, but the collision check is against the entire process-wide `h.callbacks` map, not against any per-workflow or per-owner subset: [3](#0-2) 

Because `authorizeRequest` only verifies that the caller is authorized for **their own** `workflowID` (via `h.workflowMetadataHandler.Authorize`), any caller who can trigger any workflow (their own) can supply an arbitrary `req.ID` value: [4](#0-3) 

The only validation on `requestID` is that it is non-empty and does not contain `/`: [5](#0-4) 

Consequently, an attacker who is authorized only for **their own** workflow can call the HTTP trigger endpoint with `id = <victim's requestID>` before the victim does. This inserts an entry into the shared `h.callbacks` map under that key. When the legitimate owner (of a completely different workflow) later submits their own authorized request using that same `requestID`, `setupCallback` finds the key already occupied and rejects the legitimate request with `jsonrpc.ErrConflict`, exactly mirroring how `Registry.register` let an attacker pre-occupy a `SafeGuard` address and made the legitimate `createSafeGuard` call revert.

### Impact Explanation
This allows a low-privilege caller (anyone who owns/controls at least one workflow able to reach this HTTP trigger endpoint) to selectively deny service to another, unrelated workflow's execution request, provided the attacker can predict or learn the victim's `requestID` (e.g., a client-chosen idempotency key, sequential counter, or a value derived from a predictable business process such as an order/invoice number). The victim's legitimate trigger request never executes and is returned a `Conflict` error, exactly matching the "unauthorized denial of a legitimate registration/run" bug class the report describes, but here applied to blocking a workflow run.

### Likelihood Explanation
Exploitation requires the attacker to (a) be authorized to trigger at least one workflow through this gateway path, and (b) predict or learn a `requestID` the victim intends to use. Because `requestID` is entirely client-chosen and unscoped from workflow/owner identity, and many integrations use predictable or sequential IDs (order numbers, timestamps, counters), this is a realistic namespace-collision griefing vector reachable from an unprivileged, non-operator client of the gateway.

### Recommendation
Scope the pending-request map key by `(workflowID or workflowOwner, requestID)` instead of `requestID` alone, so that a caller can only collide with entries belonging to workflows they are already authorized to affect. This closes the cross-tenant griefing vector while preserving per-request idempotency within a single workflow/owner's namespace — directly analogous to how PR #10's fix removed the globally-writable `Registry` and moved registration under the exclusive control of the entity that should own that namespace.

### Proof of Concept
1. Workflow owner **A** ("victim") plans to send an authorized HTTP trigger request to their workflow with `id = "order-1042"` (a predictable/business-derived value).
2. Attacker **B**, who owns an unrelated workflow, sends their own valid, authorized HTTP trigger request (`workflowID` = B's own workflow) with `id = "order-1042"` first. `authorizeRequest` succeeds because B is validly authorized for B's own workflow; `setupCallback` inserts `h.callbacks["order-1042"]`.
3. Victim A's request with the same `id = "order-1042"` arrives afterward. `setupCallback` finds `h.callbacks["order-1042"]` already present and returns `jsonrpc.ErrConflict`, and A's workflow trigger is rejected (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go` lines 423-426), even though A had no interaction with B's workflow and no way to detect the collision in advance.

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L58-66)
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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-456)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}

	// Build one response aggregator per shard the workflow is assigned to.
	assigned := h.workflowMetadataHandler.WorkflowShards(workflowID)
	if len(assigned) == 0 {
		// this shouldn't happen because we checked it in authorizeRequest()
		h.handleUserError(ctx, requestID, jsonrpc.ErrInternal, fmt.Sprintf("Workflow %s is not assigned to any DONs", workflowID), callback)
		return nil, errors.New("workflow is not assigned to any shards")
	}

	aggregators := make(map[string]*aggregation.IdenticalNodeResponseAggregator, len(assigned))
	for _, shard := range assigned {
		// (N+F)//2 + 1 threshold where N = number of nodes, F = number of faulty nodes
		threshold := (len(shard.members)+shard.f)/2 + 1
		agg, err := aggregation.NewIdenticalNodeResponseAggregator(threshold)
		if err != nil {
			return nil, errors.New("failed to create response aggregator: " + err.Error())
		}
		aggregators[shard.donID] = agg
	}

	doneCh := make(chan struct{})
	h.callbacks[requestID] = savedCallback{
		Callback:            callback,
		requestStartTime:    requestStartTime,
		createdAt:           time.Now(),
		responseAggregators: aggregators,
		doneCh:              doneCh,
	}
	return doneCh, nil
}
```
