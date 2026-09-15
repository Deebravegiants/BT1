### Title
Global (unscoped) request-ID namespace in the Gateway HTTP trigger handler allows any authorized workflow caller to grief another user's trigger request - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Folks Finance report describes a griefing bug where a user-chosen identifier (`accountId`) is stored in a single global namespace with no per-user scoping, letting an unprivileged attacker "claim" the same ID before the legitimate owner and permanently block their operation. The chainlink Gateway's `httpTriggerHandler` has the same structural flaw: the client-supplied JSON-RPC `id` (request ID) is used as the sole key into a single map (`h.callbacks`) that is shared across *all* workflows and owners served by a DON, rather than being scoped per workflow/owner. Any caller who can get one request authorized against any workflow on that DON can occupy an arbitrary request ID string and cause a different, unrelated user's request bearing the same ID to be rejected.

### Finding Description
`HandleUserTriggerRequest` processes requests in this order: parse/validate → `resolveWorkflowID` → `authorizeRequest` (checks the caller is authorized for *their own* target `workflowID`) → `checkRateLimit` → `setupCallback`. [1](#0-0) 

`setupCallback` is where the request ID collision is checked, and it operates on a handler-wide map keyed only by the raw request ID string, with no workflow or owner component in the key: [2](#0-1) 

```go
type httpTriggerHandler struct {
    ...
    callbacksMu sync.Mutex
    callbacks   map[string]savedCallback // requestID -> savedCallback
    ...
}
``` [3](#0-2) 

`validateRequestID` only rejects empty IDs or IDs containing `/`; any other client-chosen string is accepted as-is: [4](#0-3) 

Because `authorizeRequest` only checks that the caller is authorized for *the workflow they specify in their own request* (`h.workflowMetadataHandler.Authorize(workflowID, req.Auth, req)`), an attacker does not need any relationship to the victim's workflow. The attacker only needs a valid, authorized request against *some* workflow on the same DON, and can choose the request ID freely: [5](#0-4) 

If the attacker submits (or races to submit) a trigger request using the same `id` string that a victim intends to use—guessed, predictable (timestamps, sequence numbers, common tokens), or otherwise obtained—the victim's later call to `setupCallback` finds the ID already present and rejects the victim's request with a user-facing conflict error, exactly mirroring the `AccountAlreadyCreated` revert in the reported smart-contract bug:
```go
if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict,
      fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
``` [6](#0-5) 

This is analogous to the `AccountManager.createAccount` bug: a user-supplied identifier is checked/claimed in a single shared table (`accounts[accountId]` on-chain vs `h.callbacks[requestID]` in the gateway) with no per-caller partitioning, so any authorized caller can pre-empt another caller's use of that identifier. Notably, the vault gateway handler was built to avoid exactly this class of bug: it namespaces the active-request map key by owner (`owner + Separator + requestID`), as shown in its test: [7](#0-6) 
The confidential-relay handler and the HTTP trigger handler, however, key their in-flight-request maps purely by the raw client-supplied `req.ID` with no owner/workflow component: [8](#0-7) 

### Impact Explanation
This is a griefing/denial-of-service vector with no profit motive required for the attacker, matching the report's "Griefing" impact category. Any party that can obtain authorization for at least one workflow on a shared DON (which may be a low-barrier or even self-registered workflow) can:
- Preemptively occupy request-ID strings that other users are likely to use (default clients, timestamp-based IDs, low-entropy IDs), causing their legitimate `workflows.execute` HTTP-trigger calls to fail with `ErrConflict`.
- Repeat this at will since the attack costs the attacker only their own rate-limit budget, not the victim's, while denying the victim service until the entry is reaped/timed out (entries persist in `h.callbacks` until processed or reaped by the async reaper, per the `processed`/`doneCh` bookkeeping in `savedCallback`). [9](#0-8) 

The damage is limited to availability/service disruption of specific trigger requests (not fund loss or secret disclosure), consistent with the "Griefing" classification used in the reference report.

### Likelihood Explanation
Exploitability depends on the attacker being able to predict or observe the request ID the victim will use before the victim's request lands. Chainlink Gateway request IDs are entirely client-chosen strings with essentially no server-side entropy requirement (only non-empty, no `/`), so:
- If client tooling uses low-entropy or predictable IDs (sequence counters, timestamps rounded to a coarse resolution, fixed default strings such as `"1"`, `"test"`), an attacker can pre-claim likely values with negligible cost.
- Even without prediction, an attacker who is racing against a known target request (e.g., observed via logs, shared infra, or known integration patterns) can win the race since there is no leader-election or per-caller partition to protect the victim's request.

This is lower likelihood than the on-chain original (which had full mempool visibility for perfect front-running), because the Gateway has no public mempool equivalent; the attacker must guess/predict or otherwise learn the ID rather than observe it deterministically. This uncertainty (how request IDs are generated by the various Gateway clients, and how tight the reaper's TTL is) could not be fully verified within the available context and would need to be checked further, e.g., in the reaper/TTL configuration referenced by `createdAt`/`processed` fields, which was not retrievable before the tool budget was exhausted.

### Recommendation
Scope the in-flight-request de-duplication key by workflow/owner in addition to the client-supplied request ID (as already done in the vault handler, which uses `owner + Separator + requestID`), e.g. key `h.callbacks` by `(workflowOwner, workflowID, requestID)` or a hash thereof instead of `requestID` alone. This ensures a caller can only collide with request IDs within their own workflow/owner namespace, eliminating the ability for an unrelated party to occupy another user's request ID and block their legitimate trigger. Apply the same fix to the confidential-relay handler's `activeRequests` map, which has the identical unscoped-key pattern.

### Proof of Concept
Conceptual PoC (cannot be executed here, but derivable directly from the code paths above):
1. Attacker registers/owns Workflow A (or uses any workflow they are authorized to trigger) on DON `X`.
2. Attacker predicts/guesses that Victim will submit an HTTP trigger request to Workflow B (also on DON `X`) using request ID `"victim-req-1"` (e.g., a commonly used or timestamp-derived ID).
3. Attacker sends a valid, authorized `workflows.execute` request for Workflow A with JSON-RPC `id = "victim-req-1"`. This passes `authorizeRequest` (attacker is authorized for their own Workflow A) and `setupCallback` inserts `h.callbacks["victim-req-1"] = ...`.
4. Victim sends their legitimate `workflows.execute` request for Workflow B with `id = "victim-req-1"`. `setupCallback` finds the key already present (regardless of the fact that it belongs to a different workflow/owner) and returns `ErrConflict`, denying the victim's request:
```go
if _, found := h.callbacks[requestID]; found {
    h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, ...)
    return nil, fmt.Errorf("in-flight request ID: %s", requestID)
}
``` [6](#0-5) 

This is directly mirrored by the existing "duplicate request ID" unit test in the repo, which demonstrates the collision behavior (though within a single workflow in the test) and confirms the map is keyed purely by `requestID`: [10](#0-9)

### Citations

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L43-56)
```go
type savedCallback struct {
	handlers.Callback
	requestStartTime time.Time
	createdAt        time.Time
	// processed is set once the aggregated response has been sent to the user.
	// The entry stays in the callbacks map so late node responses can be told
	// apart from unknown request IDs, and is removed later by the async reaper.
	processed bool
	// responseAggregators holds one IdenticalNodeResponseAggregator per shard the
	// workflow is assigned to, keyed by shard donID. The first shard to reach its
	// quorum produces the user response.
	responseAggregators map[string]*aggregation.IdenticalNodeResponseAggregator
	doneCh              chan struct{} // closed when callback is responded to (processed) or reaped unanswered. signals sendWithRetries to stop retrying
}
```

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L419-427)
```go
func (h *httpTriggerHandler) setupCallback(ctx context.Context, requestID string, callback handlers.Callback, requestStartTime time.Time, workflowID string) (<-chan struct{}, error) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()

	if _, found := h.callbacks[requestID]; found {
		h.handleUserError(ctx, requestID, jsonrpc.ErrConflict, fmt.Sprintf("requestID: %s has already been used. Ensure the requestID is unique for each request.", requestID), callback)
		return nil, fmt.Errorf("in-flight request ID: %s", requestID)
	}

```

**File:** core/services/gateway/handlers/vault/handler_test.go (L736-750)
```go
		expectedRequestID := owner + vaulttypes.RequestIDSeparator + requestID
		response := jsonrpc.Response[json.RawMessage]{
			ID:     expectedRequestID,
			Result: (*json.RawMessage)(&resultBytes),
			Method: vaulttypes.MethodSecretsList,
		}
		resultBytes, err = json.Marshal(responseData)
		require.NoError(t, err)

		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.NoError(t, err)

		// send duplicate request
		err = h.HandleJSONRPCUserMessage(t.Context(), validJSONRequest, callback)
		require.ErrorContains(t, err, "request was already authorized previously")
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-430)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
	ar := &activeRequest{
		Callback:  callback,
		req:       req,
		labels:    labels,
		createdAt: h.clock.Now(),
		responses: map[string]*jsonrpc.Response[json.RawMessage]{},
	}
	h.activeRequests[req.ID] = ar
	return ar, nil
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L320-358)
```go
	t.Run("duplicate request ID", func(t *testing.T) {
		handler, mockDon := createTestTriggerHandler(t)
		privateKey := createTestPrivateKey(t)
		registerWorkflow(t, handler, workflowID, privateKey)
		callback1 := hc.NewCallback()
		callback2 := hc.NewCallback()

		triggerReq := gateway_common.HTTPTriggerRequest{
			Workflow: gateway_common.WorkflowSelector{
				WorkflowID: workflowID,
			},
			Input: []byte(`{"key": "value"}`),
		}
		reqBytes, err := json.Marshal(triggerReq)
		require.NoError(t, err)

		rawParams := json.RawMessage(reqBytes)
		req := &jsonrpc.Request[json.RawMessage]{
			Version: "2.0",
			ID:      requestID,
			Method:  gateway_common.MethodWorkflowExecute,
			Params:  &rawParams,
		}
		// First request should succeed
		req.Auth = createTestJWTToken(t, req, privateKey)
		mockDon.EXPECT().SendToNode(mock.Anything, mock.Anything, mock.Anything).Return(nil).Times(3)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback1, time.Now())
		require.NoError(t, err)

		// Second request with same ID should fail
		req.Auth = createTestJWTToken(t, req, privateKey)
		err = handler.HandleUserTriggerRequest(t.Context(), req, callback2, time.Now())
		require.Error(t, err)
		require.Contains(t, err.Error(), "in-flight request")

		r, err := callback2.Wait(t.Context())
		require.NoError(t, err)
		requireUserErrorSent(t, r, jsonrpc.ErrConflict)
	})
```
