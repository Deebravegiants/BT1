## Analog Found

### Title
Cross-workflow request-ID squatting causes DoS on legitimate HTTP trigger callers - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The Chainlink CRE Gateway's HTTP trigger handler stores in-flight requests in a single, global map keyed only by the caller-supplied JSON-RPC `id` string, with no namespacing by workflow, owner, or caller identity. Any authenticated caller of *any* workflow can pre-register (squat) an arbitrary request ID before a different user's request with the same ID arrives, causing the victim's legitimate `workflows.execute` call to be rejected with a conflict error — the same "who lands first wins, the other one reverts" pattern described in the loanId collision report, just at the gateway layer instead of on-chain.

### Finding Description
`httpTriggerHandler.callbacks` is declared as a single `map[string]savedCallback // requestID -> savedCallback` shared across the entire handler instance, i.e. across every workflow served by this gateway node/DON. [1](#0-0) 

`validateRequestID` only checks that the caller-chosen ID is non-empty and doesn't contain `/`; it enforces no per-workflow or per-caller scoping and does not require the ID to be unpredictable: [2](#0-1) 

The uniqueness check happens in `setupCallback`, keyed purely by `requestID` with no workflow/owner component: [3](#0-2) 

Crucially, `setupCallback` is reached only after `authorizeRequest` — meaning the caller only needs a *valid signature for their own workflow* (any workflow, not necessarily the victim's) to reach the shared `callbacks` map: [4](#0-3) 

So the attacker does not need any privilege over the victim's workflow — they only need their own (self-service, low-privilege) workflow and knowledge/prediction of the victim's chosen request ID. If the attacker's request reaches `setupCallback` first with the same ID string, the entry is recorded in the global `callbacks` map; when the victim's genuine request for their own (different) workflow arrives with that same ID, `setupCallback` finds the key already present and rejects it: [5](#0-4) 

This exactly mirrors the reported bug class: a user-chosen identifier (`loanId` in the report, `requestID` here) is unique only in a single global namespace rather than being scoped to the caller/owner, and race-order — not authorization — decides whose otherwise-valid request succeeds. The existing test `TestHttpTriggerHandler_HandleUserTriggerRequest/"duplicate request ID"` demonstrates the mechanics of the collision/rejection path (it just doesn't test the cross-workflow angle): [6](#0-5) 

By contrast, the vault handler's active-request map is not globally raw-ID keyed the same way: request IDs there are owner-prefixed (`owner + RequestIDSeparator + requestID`), which scopes uniqueness per owner and avoids cross-user collisions: [7](#0-6) 

### Impact Explanation
An attacker who can guess, predict, or otherwise learn a victim's chosen request ID (e.g. common idempotency-key patterns, sequential IDs, IDs leaked via logs/telemetry, or simply IDs that overlap because two independent client tools use the same default scheme) can grief the victim by squatting that ID against an unrelated workflow they control. The victim's `workflows.execute` HTTP trigger call fails with `jsonrpc.ErrConflict` ("requestID: X has already been used"), forcing the victim to retry with a new ID and breaking systems that rely on the caller-chosen ID for idempotency/correlation. This is a griefing/DoS impact with no direct fund loss, matching the "Griefing" impact category of the reported bug class.

### Likelihood Explanation
Exploitability requires: (1) the attacker to control any workflow authorized to call the gateway (self-service, low bar), and (2) knowledge or prediction of the victim's request ID before the victim's request is processed. Because IDs are entirely client-chosen with only a `/`-character restriction, and no requirement for cryptographic randomness, collisions are plausible in real deployments using predictable ID schemes (timestamps, incrementing counters, deterministic idempotency keys shared across integrations). Likelihood is moderate — it depends on the attacker being able to observe or guess an ID ahead of processing — but the underlying design flaw (global unscoped map) is a definite root cause of unnecessary cross-user exposure.

### Recommendation
Scope the `callbacks` map key (and any equivalent maps in other gateway handlers using bare caller-supplied IDs, e.g. `confidentialrelay/handler.go`'s `activeRequests`) by a tuple that includes the authenticated caller/workflow identity, not just the raw client-chosen `requestID` — e.g. `(workflowID, requestID)` or `(authorizedKey, requestID)`, similar to the owner-prefixing already used in the vault handler (`owner + RequestIDSeparator + requestID`). This prevents one workflow's traffic from colliding with and blocking another's, eliminating the cross-user race entirely.

### Proof of Concept
1. Attacker deploys/owns Workflow B (any workflow they're authorized to trigger).
2. Attacker predicts or observes that Victim intends to call Workflow A's HTTP trigger with request ID `"order-12345"`.
3. Attacker sends `workflows.execute` for Workflow B with `id: "order-12345"`, which passes `authorizeRequest` (valid for Workflow B) and reaches `setupCallback`, inserting `"order-12345"` into the shared `h.callbacks` map.
4. Victim's genuine request for Workflow A with the same `id: "order-12345"` arrives at `setupCallback`; the duplicate check at [5](#0-4)  fires, and Victim receives `ErrConflict`, denying their legitimate execution.

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

**File:** core/services/gateway/handlers/vault/handler_test.go (L736-736)
```go
		expectedRequestID := owner + vaulttypes.RequestIDSeparator + requestID
```
