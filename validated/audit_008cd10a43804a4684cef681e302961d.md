### Title
Unprivileged attacker can grief/censor another user's HTTP trigger request by front-running the global `requestID` used as the gateway's callback-map key - ([File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go])

### Summary
The Chainlink Gateway's HTTP Trigger handler keys in-flight requests by a client-supplied `requestID` (the JSON-RPC `req.ID`) in a single global map, `h.callbacks`, shared across all senders/workflows. `setupCallback` rejects a request if that `requestID` already exists in the map, exactly mirroring the Omnipool bug pattern: a caller-chosen identifier that is not scoped to the caller's own identity is used as a mutex/guard, so any unprivileged client can pre-claim (front-run) an identifier that another legitimate user is about to use, causing that legitimate user's trigger request to be denied. [1](#0-0) 

### Finding Description
`HandleUserTriggerRequest` validates and authorizes a trigger request, then calls `setupCallback(ctx, req.ID, ...)`, where `req.ID` is the `requestID` supplied by the calling client in the JSON-RPC request body: [2](#0-1) 

`setupCallback` checks the shared `h.callbacks` map (keyed purely by `requestID`, with no sender/workflow scoping in the key) and rejects the call with an `ErrConflict` if an entry for that ID is already present: [1](#0-0) 

The only validation on `requestID` is non-emptiness and absence of the `/` character — there is no requirement that it be derived from the caller's identity, be unpredictable, or be namespaced per sender: [3](#0-2) 

Because `callbacks` is a single process-wide `map[string]savedCallback` (declared on `httpTriggerHandler`) with no per-sender partitioning: [4](#0-3) 

...any unauthenticated-in-the-relevant-sense client that can reach the gateway's trigger endpoint (only JWT-authorized against the *target workflow*, not against the `requestID` namespace) can submit a trigger request using a `requestID` value that it expects (or observes/guesses) a victim client to use next, and "claim" it first. When the victim's genuine request with the same `requestID` then arrives, it is rejected with `jsonrpc.ErrConflict` ("requestID has already been used...") rather than being processed, exactly like the Omnipool `lastTransactionBlock[_depositFor]` griefing: the attacker uses a caller-supplied identifier that references someone else's future action to block that action.

Unlike the original report's `_depositFor` (an address chosen entirely by the attacker, but naming the victim), here the identifier is a `requestID`; the practical severity therefore hinges on whether `requestID`s are ever predictable/reused/attacker-observable (e.g., client-generated deterministic IDs, replayed/leaked request IDs, or race conditions where two legitimate concurrent submissions from the same integration happen to choose overlapping IDs). This is a plausible, reachable analog but weaker than the original because exploitation additionally depends on the attacker being able to predict or learn the victim's `requestID` in advance, which is not guaranteed by the code shown.

### Impact Explanation
If exploited, this results in a denial-of-service for a specific, targeted trigger execution: the legitimate workflow invocation is rejected and the workflow does not run for that request, without the caller being at fault. Because the workflow gateway is meant to be internet-facing and multi-tenant (workflows execute for potentially many distinct owners/customers), a griefed request could translate into a missed/blocked workflow execution for a specific customer at chosen moments (e.g., racing to block time-sensitive triggers). This is a moderate-impact denial-of-service/censorship primitive, not fund loss or credential disclosure, so it is weaker than the classic Omnipool impact (loss of funds).

### Likelihood Explanation
Likelihood is contingent on whether `requestID` values used by real clients are ever predictable or discoverable by third parties (e.g., sequential counters, timestamps, or IDs echoed back in logs/errors that another party observes). The code does not enforce per-sender or unpredictable request IDs, so nothing in this handler itself prevents the collision from being exploitable if such predictability exists in any client implementation. Absent confirmation that all `requestID`s are cryptographically random and kept secret, this should be treated as a plausible but conditional griefing vector, lower likelihood than the original (fully attacker-chosen victim address) but still a design weakness worth mitigating.

### Recommendation
- Scope the `callbacks` map key by sender/workflow identity in addition to `requestID` (e.g., key by `(authorizedKey or workflowOwner, requestID)`), so one caller cannot pre-claim another caller's request ID.
- Alternatively, generate the deduplication key server-side (e.g., hash of sender identity + `requestID`) rather than trusting `requestID` alone as a global namespace.
- Document/enforce that `requestID` must be a client-generated random/unguessable value, and consider rate-limiting or authenticating the "claim" step so that conflict detection cannot be weaponized by a party who has no relationship with the affected workflow's authorized keys.

### Proof of Concept
1. Attacker obtains (or predicts) the `requestID` that a victim's client will use for its next `workflows.execute` call to the Gateway (e.g., due to a predictable/sequential client-side ID scheme, or by observing a previous exchange).
2. Attacker sends its own valid JSON-RPC trigger request (authorized against any workflow it itself controls or is authorized for) using that same `requestID` value before the victim's real request arrives.
3. `setupCallback` inserts the attacker's entry into `h.callbacks[requestID]`: [1](#0-0) 
4. When the victim's genuine request with the same `requestID` subsequently reaches `setupCallback`, it hits the `found` branch and is rejected with `jsonrpc.ErrConflict` and the message `"requestID: %s has already been used..."`, denying that specific trigger invocation for the victim.

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
