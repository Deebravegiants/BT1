### Title
Global (non-workflow-scoped) `requestID` namespace in the HTTP trigger handler allows any authenticated user to front-run and block another user's job-trigger request - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Sherlock report's bug class is: a permissionless/low-privilege function accepts caller-supplied parameters that mutate *shared, non-isolated* state used later to make a decision affecting a different party, and a racing/front-running caller can plant that shared state first to disadvantage the legitimate party. The `httpTriggerHandler` in the Gateway's Capabilities v2 HTTP trigger path has an analogous root cause: the `requestID` supplied by an authenticated end user is used as the sole key into a single, DON-wide `callbacks` map that is not scoped to the caller's workflow/owner identity, so any authenticated caller can pre-claim an arbitrary `requestID` string and cause a different workflow owner's legitimately-submitted request carrying the same ID to be rejected.

### Finding Description
`HandleUserTriggerRequest` validates the request, resolves the `workflowID`, authorizes the caller against *that* workflow's registered key via `authorizeRequest`, checks the per-workflow rate limit, and finally calls `setupCallback`: [1](#0-0) 

`setupCallback` stores the pending request keyed only by the user-supplied `requestID`, in a map shared across *all* workflows/owners served by this handler instance: [2](#0-1) 

```go
h.callbacksMu.Lock()
defer h.callbacksMu.Unlock()

if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. ...", requestID), callback)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
```

The `callbacks` field is declared as a single `map[string]savedCallback // requestID -> savedCallback` on the handler, with no workflow/owner dimension: [3](#0-2) 

`validateRequestID` only rejects empty IDs and IDs containing `/`; it does not require the ID to be derived from anything secret or bound to the caller's identity — it is an arbitrary user-chosen plain string, as also documented for "User Requests" in the v2 README ("Plain string identifiers (cannot contain '/')"): [4](#0-3) 

Because authorization (`authorizeRequest`) is workflow-scoped and happens *before* the ID-conflict check, and the conflict check itself is global, any user who is authorized for their *own* workflow can submit a trigger request using a `requestID` string that they expect (or can observe/predict, e.g. via monitoring, shared conventions, or simple guessing of low-entropy/sequential IDs used by another integration) another workflow owner is about to use. If the attacker's request reaches `setupCallback` first, the victim's subsequent legitimate request with the same `requestID` is rejected with `jsonrpc.ErrConflict` ("requestID ... has already been used"), denying that specific job execution — directly analogous to the Sherlock report where a racing/front-running call using attacker-controlled parameters overwrites shared accounting state and diverts an outcome away from the attacker and onto the victim.

### Impact Explanation
This is a request-impersonation/quota-bypass-style denial: an authenticated but otherwise unprivileged caller (only authorized for their own workflow) can, by racing a shared global namespace, block another tenant's specific job trigger execution from being processed by the gateway/DON for that request ID, without needing to compromise the victim's credentials. This matches the "concrete ... request impersonation, allowlist/quota bypass, or cross-user response confusion" bar from the validation rules — here it is a cross-tenant griefing/DoS enabled by a shared mutable resource keyed on attacker-controlled input, the same root cause pattern as the Sherlock finding (shared state updated by an untrusted party's chosen parameters, racing to disadvantage another party). It does not directly move funds, but it can prevent a legitimate workflow execution from running, which for time-sensitive triggers (e.g., price/oracle-driven workflows) has real operational impact.

### Likelihood Explanation
Exploitation requires: (1) the attacker to hold valid credentials for *some* workflow served by the same handler instance (any registered workflow, not the victim's), and (2) the attacker to know or predict the victim's chosen `requestID` before the victim's request lands. Request IDs are caller-chosen application-level strings (often sequential counters, timestamps, or otherwise low-entropy values used by client SDKs), so guessing/observing is plausible in many integration patterns even though not guaranteed. This keeps likelihood at low-to-medium, similar to the original report's framing ("MEDIUM, as the attack can only be performed when specific conditions are met").

### Recommendation
Scope the `callbacks` map (and the corresponding conflict check) by `(workflowID, requestID)` or `(workflowOwner, requestID)` instead of a bare `requestID`, so that one tenant's chosen ID can never collide with, and therefore never block, another tenant's request. Alternatively, derive the internal dedup key deterministically from the authorized `workflowID` plus the user-supplied ID (similar to how `executionIDWithTriggerIndex`/`legacyExecutionID` are already generated from `workflowID` + `req.ID`) before using it as the map key in `setupCallback`.

### Proof of Concept
1. Attacker registers/owns Workflow A and obtains valid JWT auth for it (any legitimately provisioned workflow works, per `authorizeRequest`).
2. Attacker learns or predicts that Victim's Workflow B client will shortly submit a trigger request with `requestID = "order-12345"` (e.g., because Victim's client uses monotonically increasing or otherwise low-entropy IDs).
3. Attacker sends a `workflowExecute` JSON-RPC request for Workflow A with `id = "order-12345"`. It passes `validateRequestID`, `resolveWorkflowID`, `authorizeRequest` (against Workflow A, which attacker is authorized for), `checkRateLimit`, and reaches `setupCallback`, which inserts `h.callbacks["order-12345"]`.
4. Victim's genuine request for Workflow B with `id = "order-12345"` arrives afterward; `setupCallback` finds the key already present and returns `jsonrpc.ErrConflict` to the victim, per lines 423-426 of `http_trigger_handler.go`, and the victim's execution is never dispatched to the DON.

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L190-200)
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
