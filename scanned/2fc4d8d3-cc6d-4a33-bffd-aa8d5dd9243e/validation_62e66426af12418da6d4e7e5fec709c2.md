## Analog Found

### Title
Global, caller-controlled `requestID` deduplication in the HTTP trigger gateway handler enables cross-user DOS via ID squatting - (File: core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go)

### Summary
The gateway's `httpTriggerHandler` deduplicates in-flight requests using a single global map keyed solely by the client-supplied JSON-RPC `id` (`req.ID`), with no per-workflow or per-caller namespacing. Any unprivileged caller who can predict or observe another user's `requestID` before it lands in the map can pre-register that same ID first, causing the legitimate request to be rejected with a "conflict" error — a direct analog of the `_deduplicateOrder`/nonce front-running DOS described in the report, where a caller-chosen replay key collides across unrelated callers.

### Finding Description
`httpTriggerHandler.callbacks` is declared as a single global map, `requestID -> savedCallback`, shared across *all* workflows and callers: [1](#0-0) 

The only pre-insertion validation of `requestID` performed in `validateRequestID` checks for non-empty and absence of `/`; it does not scope the ID to the caller's identity, workflow, or org: [2](#0-1) 

The dedup check itself is a raw lookup on that global map, keyed by the bare `requestID`: [3](#0-2) 

This mirrors the `_deduplicateOrder` root cause in the report exactly: a replay/duplicate guard whose key (`order.nonce`/`order.benefactor` there, `req.ID` here) is entirely attacker-supplied and not scoped to the legitimate caller, so an unrelated third party can "claim" the key first and cause the victim's real request to be rejected as a duplicate. Note that a sibling handler in the same codebase, the vault handler, avoids this exact pattern by prefixing the dedup key with the owner (`owner + vaulttypes.RequestIDSeparator + requestID`), as shown in its test: [4](#0-3) 

The HTTP trigger handler has no equivalent owner/workflow-scoped prefixing before `setupCallback` inserts into the shared map, at `HandleUserTriggerRequest` line 141: [5](#0-4) 

### Impact Explanation
Any unprivileged caller of the internet-facing gateway's HTTP trigger endpoint can deny service to a specific, targeted request by submitting a request with the same `requestID` before the victim's request is processed and removed from the map. Because JSON-RPC request IDs are frequently predictable (sequential counters, timestamps, or client-generated UUIDs that may be logged/observed elsewhere), and the map is global across all workflows/owners, this is a low-cost, unauthenticated-adjacent DOS vector against a specific caller's workflow execution request — analogous to the reported nonce-collision DOS on mint/redeem.

### Likelihood Explanation
The barrier to exploitation is low: the attacker needs no special privileges, only the ability to send an HTTP trigger request with a chosen `id` field and knowledge (or a guess) of the target `requestID`. `validateRequestID` performs no uniqueness-per-caller enforcement, so any value that passes the trivial checks (non-empty, no `/`) can be squatted on.

### Recommendation
Namespace the dedup key by an identity that only the legitimate caller controls (e.g., prefix/derive the internal callback-map key from the resolved workflow/owner plus `req.ID`, similar to the vault handler's `owner + RequestIDSeparator + requestID` pattern) instead of using the raw, fully attacker-controlled `req.ID` as the sole key into a globally shared map.

### Proof of Concept
1. Attacker learns or predicts victim's upcoming `requestID` value `X` for workflow `W`.
2. Attacker sends a valid `workflows.execute` HTTP trigger request with `id = X` (any workflow it is authorized for, or even its own).
3. `setupCallback` inserts `X` into the global `h.callbacks` map.
4. Victim's genuine request with the same `id = X` for workflow `W` arrives at `HandleUserTriggerRequest` → `setupCallback`, finds `X` already present, and is rejected with `jsonrpc.ErrConflict` ("requestID: X has already been used...").
5. Victim's legitimate workflow execution never dispatches, achieving a targeted DOS. [6](#0-5)

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L141-144)
```go
	doneCh, err := h.setupCallback(ctx, req.ID, callback, requestStartTime, workflowID)
	if err != nil {
		return err
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

**File:** core/services/gateway/handlers/vault/handler_test.go (L736-736)
```go
		expectedRequestID := owner + vaulttypes.RequestIDSeparator + requestID
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
