### Title
Unprivileged request-ID squatting blocks legitimate HTTP-trigger workflow execution - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The reported Solidity bug shows a critical function's guard condition (`value == 0 || value >= minStakeAmount`) being derived from externally-mutable state (a token balance) that an unprivileged attacker can perturb by front-running, permanently breaking the legitimate caller's intended condition. The analogous pattern in this codebase is the gateway's HTTP-trigger callback bookkeeping, which uses a **globally shared, attacker-controlled key** (the JSON-RPC request `ID`) as the sole means of admitting or rejecting a legitimate workflow-execution request.

### Finding Description
`httpTriggerHandler.HandleUserTriggerRequest` accepts a caller-supplied `req.ID` and, after authorization/rate-limit checks, calls `setupCallback` which enforces uniqueness against a single, gateway-wide map: [1](#0-0) 

```go
func (h *httpTriggerHandler) setupCallback(...) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}
	...
```

The `requestID` value comes directly from the untrusted client request and is validated only for non-emptiness and absence of `/`: [2](#0-1) 

Critically, `callbacks map[string]savedCallback` is declared and keyed globally — not scoped per user, per workflow owner, or per workflow ID: [3](#0-2) 

Because any unprivileged HTTP client reaching the gateway's trigger endpoint can submit a request with an arbitrary `ID` for any workflow, an attacker who predicts or otherwise knows a request ID a victim intends to use (e.g., an idempotency key, invoice ID, or deterministic identifier used by the calling system) can preemptively register that same ID against the shared map. The victim's subsequent legitimate request will then hit the `found` branch and be rejected with `jsonrpc.ErrConflict`, exactly mirroring the Solidity bug where an attacker's cheap, unprivileged action (sending a small token / here, sending a cheap trigger request) permanently invalidates the condition a legitimate actor depends on to proceed.

### Impact Explanation
This is a griefing/denial-of-service vector against workflow execution triggered via the gateway's HTTP trigger path — the "critical function" analog to `_stake`. A legitimate workflow invocation can be blocked for the lifetime of the squatted callback entry (until the response doneCh closes or the periodic reaper evicts it), causing failed/delayed executions for a specific caller without requiring any privilege beyond the ability to send an HTTP trigger request (subject to normal auth/rate-limit checks that any workflow caller must already pass).

### Likelihood Explanation
Exploitability depends entirely on whether request IDs are predictable/guessable by third parties. If calling systems use random UUIDs, the collision is unlikely to be exploited in practice. However, if request IDs are derived from externally observable or deterministic values (a common idempotency-key pattern), this becomes trivially exploitable by any unprivileged actor with knowledge of that ID, requiring only a cheap request sent before the legitimate one — the same "front-run" precondition as the original report. I could not verify from the available code how calling systems generate `req.ID` in practice, so likelihood is uncertain and depends on caller-side ID generation practices outside this repo.

### Recommendation
Scope the in-flight callback uniqueness check by a composite key that includes an untrusted-but-uncontrollable component (e.g., `workflowID`/`workflowOwner` plus an internally generated or hashed value), rather than relying solely on the raw, attacker-supplied `requestID`. Alternatively, bind uniqueness enforcement to the authenticated caller/key so requestID collisions can only occur within a single caller's own namespace, preventing cross-user request-ID squatting.

### Proof of Concept
1. Attacker learns (or predicts) the `requestID` a victim's calling system will use for its next HTTP-trigger workflow-execute request (e.g., a deterministic idempotency key).
2. Attacker sends a valid, minimal JSON-RPC `workflows.execute` request to the gateway's HTTP trigger endpoint using that same `requestID`, targeting any workflow it is authorized to call. This passes `validateRequestID`, `authorizeRequest`, and `checkRateLimit`, and reaches `setupCallback`, inserting the entry into the global `h.callbacks` map.
3. Victim's legitimate request with the same `requestID` arrives shortly after and reaches `setupCallback`; the `found` check triggers, and the victim receives `jsonrpc.ErrConflict` ("requestID … has already been used"), failing to execute its workflow.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-434)
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
```
