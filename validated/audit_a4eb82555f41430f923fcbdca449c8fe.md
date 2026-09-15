The report's bug class — arbitrary user-chosen identifiers combined with global first-writer-wins state that causes a legitimate request to be rejected/griefed — has a direct analog in the CRE Gateway's HTTP trigger handler.

### Title
Cross-tenant request-ID collision allows any gateway client to grief another user's workflow trigger request - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The `httpTriggerHandler` keys its in-flight-request callback map solely by the client-supplied JSON-RPC `id` field, with no scoping by workflow, workflow owner, or authenticated key. Any unprivileged gateway client can pre-empt another tenant's request by submitting a `workflows.execute` request with the same `id` first, causing the victim's legitimate request to be rejected with a conflict error — the same "arbitrary user-chosen ID + first writer wins" pattern described in the external report's loan-creation front-running scenario.

### Finding Description
`HandleUserTriggerRequest` validates the request ID only for emptiness and absence of `/`: [1](#0-0) 

The ID is otherwise a fully attacker-controlled string. After per-workflow auth and rate-limiting, `setupCallback` registers the callback keyed purely by this string in a handler-wide map shared by *all* workflows/tenants served by this gateway node: [2](#0-1) 

```go
if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used...", requestID), callback)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
```

The map `callbacks map[string]savedCallback` is declared as global to the handler instance (`// requestID -> savedCallback`), not partitioned by workflow ID or authorized key: [3](#0-2) 

Because authorization (`authorizeRequest`) happens *before* `setupCallback` and is scoped to the caller's own workflow, an attacker only needs valid credentials for *any* workflow they control — they don't need to compromise the victim's workflow. If the attacker submits a request with the same `id` string as a victim's pending or about-to-be-sent request, the second submission (whichever arrives second, regardless of tenant) is rejected via `jsonrpc.ErrConflict`. This mirrors the reported vulnerability precisely: an arbitrary, user-chosen identifier is used as a global uniqueness key with no per-caller/per-resource partitioning, letting one unprivileged party block another's legitimate request purely by ID collision.

### Impact Explanation
This is a griefing/denial-of-service vector against the internet-facing Gateway: any authenticated (but otherwise unprivileged relative to the victim) workflow owner can deny another tenant's `workflows.execute` HTTP trigger call by racing to register the same `id` first. Because request IDs are typically predictable in practice (many client SDKs use simple counters, timestamps, or short human-chosen strings such as `"req-1"`), an attacker does not need to observe network traffic — they can simply flood common/likely ID values ahead of time to occupy slots in the shared map, or repeatedly race a specific tenant's known ID pattern. This directly matches the report's stated impact category of "Griefing (e.g. no profit motive for an attacker, but damage to the users or the protocol)."

### Likelihood Explanation
Likelihood is moderate: exploitation requires the attacker to have some valid gateway credentials (for their own workflow) but does not require any privilege over the victim's workflow, secrets, or DON membership. Since request ID uniqueness is enforced globally rather than per-workflow/per-owner, and IDs are fully user-chosen strings, collision is easy to engineer deliberately (e.g., pre-registering a batch of likely/common IDs), making this practically exploitable by any unprivileged Gateway client.

### Recommendation
Scope the in-flight request uniqueness key by `(workflowID, authorizedKey/owner, requestID)` instead of `requestID` alone, e.g. compose the map key from the resolved `workflowID` and requester identity before checking for a duplicate in `setupCallback`. This prevents one tenant's request IDs from ever colliding with another tenant's, closing the cross-tenant griefing vector while preserving the existing conflict-detection behavior for genuine duplicate resubmissions from the same caller/workflow.

### Proof of Concept
1. Attacker registers/owns Workflow A on the same Gateway node and obtains a valid signed request for `workflows.execute` with `id = "victim-id"`.
2. Victim (owner of unrelated Workflow B) is about to submit (or has just submitted) a legitimate `workflows.execute` request also using `id = "victim-id"` (e.g., a predictable/sequential ID from their client SDK).
3. Attacker's request reaches `setupCallback` first and inserts `h.callbacks["victim-id"]`, shown at: [4](#0-3) 
4. When the victim's request arrives, `setupCallback` finds the ID already present and returns `jsonrpc.ErrConflict` ("requestID: victim-id has already been used..."), causing the victim's legitimate workflow trigger to fail — despite the victim having no relationship to Workflow A or the attacker.

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
