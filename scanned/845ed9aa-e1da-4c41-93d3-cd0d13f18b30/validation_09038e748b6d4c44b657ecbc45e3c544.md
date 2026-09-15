### Title
Denial of Service via requestID Front-Running/Squatting in Gateway HTTP Trigger Handler - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Capabilities Gateway's HTTP trigger handler keys all in-flight callbacks by the raw, caller-supplied JSON-RPC `id` (`requestID`) in a single global map shared across every workflow and every caller on the node. Because the uniqueness check is performed on this unscoped, attacker-choosable string, any unprivileged client that can reach the gateway can "squat" on a `requestID` that another legitimate user is about to use (or is concurrently using), causing the victim's genuine request to be rejected outright. This mirrors the reported `loanId` collision/front-running DoS pattern: a caller-chosen identifier is checked for uniqueness with no ownership/scoping, so a second party's identical identifier causes the first (or second) legitimate request to fail.

### Finding Description
`HandleUserTriggerRequest` processes each incoming trigger request and, deep in the flow, calls `setupCallback`, which stores the pending callback keyed purely by `requestID`: [1](#0-0) 

The map itself is declared as `callbacks map[string]savedCallback // requestID -> savedCallback` — a single node-wide map, not partitioned by workflow ID, workflow owner, or authorization key: [2](#0-1) 

The only validation performed on `requestID` before it is used as the map key is that it is non-empty and does not contain `/`; it does not need to be random, unpredictable, or in any way bound to the caller's identity: [3](#0-2) 

Because `authorizeRequest` validates each caller's own signature/auth token independently of the `requestID` value, two entirely different, independently-authorized (but both unprivileged) callers can submit requests carrying the same `requestID`. Whichever request reaches `setupCallback` first wins the map slot; the second is rejected with `jsonrpc.ErrConflict` ("requestID: %s has already been used"), exactly analogous to the `UserLoanAlreadyCreated` revert in the reported bug: [4](#0-3) 

An attacker does not need to guess a victim's identifier out of thin air to cause damage broadly — they only need to predict or observe (e.g., via UI defaults, shared tooling, retried client libraries producing deterministic IDs, or simple brute-force races on short-lived/aligned IDs) a `requestID` value that a targeted or arbitrary victim workflow is likely to use, and race to claim it first, or simply flood the same fixed value repeatedly against a rate-limited but non-scoped keyspace. The same unscoped-global-map pattern also exists in the sibling handlers `core/services/gateway/handlers/vault/handler.go` (`newActiveRequest`) and `core/services/gateway/handlers/confidentialrelay/handler.go`, both of which reject a request outright if `req.ID` already exists in a global `activeRequests`-style map, confirming this is a systemic pattern in the gateway rather than an isolated slip.

### Impact Explanation
A victim's legitimate, correctly-authorized HTTP trigger request is rejected with an internal-error-class response (`jsonrpc.ErrConflict`) purely because an unrelated party used the same `requestID` string. This is a griefing/DoS impact: the victim's workflow execution never starts even though they did everything correctly, they incur wasted round-trip cost, and (depending on client retry/idempotency semantics) may believe their execution was already accepted when it was not. Because the map is gateway/node-wide rather than scoped per workflow/owner, the blast radius is not limited to attacker-vs-self collisions — any two distinct callers across the whole gateway can collide.

### Likelihood Explanation
Exploitation only requires the attacker to be a normal, authenticated (but unprivileged relative to the victim) API caller of the gateway — no special role or node compromise is needed. The attacker must know or predict the victim's `requestID`, which is plausible in common integration patterns (deterministic/incrementing IDs from client SDKs, well-known default values, or simply racing many guesses against a target window), making this a realistic, low-cost griefing vector once the target's ID pattern is known.

### Recommendation
Scope the callback/uniqueness key by caller identity in addition to the raw `requestID` (e.g., `(workflowOwner, workflowID, requestID)` or an authorization-key-derived namespace) rather than by the bare client-supplied string, so that one caller's ID choice cannot collide with another caller's request. Apply the same fix to the analogous global maps in `core/services/gateway/handlers/vault/handler.go` and `core/services/gateway/handlers/confidentialrelay/handler.go`.

### Proof of Concept
1. Legitimate user Alice, authorized for `workflowOwner=A/workflowID=W1`, prepares to send a `workflows.execute` HTTP trigger request with JSON-RPC `id = "req-42"`.
2. Attacker Bob, independently authorized for his own `workflowOwner=B/workflowID=W2`, sends his own valid trigger request using the same `id = "req-42"` slightly before Alice's request reaches `setupCallback`.
3. Bob's request passes `authorizeRequest`/`checkRateLimit` (using his own valid credentials) and calls `setupCallback`, which inserts `h.callbacks["req-42"]` successfully.
4. Alice's request then reaches `setupCallback`; the check at `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:423-426` finds `"req-42"` already present and returns `jsonrpc.ErrConflict` to Alice via `handleUserError`, even though Alice's request was fully valid and unrelated to Bob's workflow.
5. Alice's execution never starts; she must detect the failure and retry with a different ID, having wasted the round trip and any client-side timeout budget — the intended DoS outcome.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L95-146)
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
