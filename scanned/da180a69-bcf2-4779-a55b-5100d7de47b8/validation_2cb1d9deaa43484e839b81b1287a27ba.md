I found a strong analog. The gateway's legacy WebAPI handler `HandleLegacyUserMessage` in `core/services/gateway/handlers/capabilities/handler.go` explicitly has a `// TODO: apply allowlist and rate-limiting here` comment right at the point where it accepts messages from unprivileged external users and fans them out to every DON node, with no rate limiter, no allowlist, and no duplicate-message check applied before broadcasting.

### Title
Missing rate-limiting/allowlist on legacy WebAPI user messages allows unmetered flooding of all DON nodes - (File: core/services/gateway/handlers/capabilities/handler.go)

### Summary
The SEDA report describes an unmetered-message flooding vector: a check in the AnteHandler grants free gas to Commit/Reveal messages without checking for duplicates, letting an attacker flood validators cheaply. In `chainlink`, the Gateway's legacy WebAPI capabilities handler (`handler.HandleLegacyUserMessage`) accepts messages directly from external, unauthenticated/unprivileged HTTP clients and unconditionally fans each one out to every DON member — explicitly marked with `// TODO: apply allowlist and rate-limiting here` — with no per-sender rate limiter, no allowlist check, and no duplicate-message dedup before the expensive fan-out and `savedCallbacks` bookkeeping occurs.

### Finding Description
`HandleLegacyUserMessage` is reached from the Gateway's user-facing HTTP server for the `web_api_trigger` legacy method. It performs payload decoding and a staleness check, but then reaches the explicit `// TODO: apply allowlist and rate-limiting here` marker before broadcasting the message to every DON member via `don.SendToNode` in a loop over `h.donConfig.Members`, and it registers an entry in the shared `h.savedCallbacks` map keyed by `msg.Body.MessageID`. [1](#0-0) 

Unlike the sibling node-facing path `handleWebAPIOutgoingMessage`, which explicitly checks `h.nodeRateLimiter.Allow(nodeAddr)` before doing any work, the user-facing legacy path has no equivalent check at all. [2](#0-1) 

The only safety net is a periodic, size-bounded prune of `savedCallbacks` (age-based expiry plus an eviction to `maxSize/2` when the map grows too large), which is a mitigation for unbounded memory growth but does not prevent CPU/network amplification: every accepted user message is forwarded to *all* DON members regardless of how many identical or rapid-fire messages a single unauthenticated sender submits. [3](#0-2) 

This mirrors the SEDA root cause structurally: a message-acceptance path that is supposed to have an anti-abuse gate (free-gas eligibility checking for duplicates in SEDA; allowlist/rate-limiting here) but the gate is either incomplete or explicitly deferred, allowing a single unprivileged actor to trigger fan-out work to the entire node set for "free" (i.e., without passing through any throttle).

### Impact Explanation
An unauthenticated external client hitting the Gateway's legacy WebAPI trigger endpoint can send an unbounded volume of `web_api_trigger` messages. Each one is forwarded to every member of the workflow DON (`don.SendToNode` for all `h.donConfig.Members`), multiplying a single request into N node-directed messages, and adds bookkeeping to a shared in-memory map guarded only by periodic pruning. This can be used to flood DON nodes with request traffic and to grow (and repeatedly churn) the gateway's `savedCallbacks` map, degrading gateway and node availability — an availability/DOS-class impact analogous to the SEDA validator-flooding bug.

### Likelihood Explanation
The `HandleLegacyUserMessage` path is reachable directly from external, unprivileged HTTP clients calling the Gateway's user server (no signature/allowlist verification is performed in this function besides basic payload/timestamp checks), and the code contains an explicit acknowledgment (`TODO: apply allowlist and rate-limiting here`) that the intended protection is not yet implemented, making exploitation straightforward for any external caller who can reach the Gateway's public endpoint.

### Recommendation
Implement the rate-limiting and allowlist controls that are referenced by the existing TODO before the fan-out step in `HandleLegacyUserMessage` — e.g., apply a per-sender/global rate limiter (as is already done symmetrically for node-originated messages via `h.nodeRateLimiter`) and validate the sender against a configured allowlist prior to broadcasting to `h.donConfig.Members` and inserting into `h.savedCallbacks`. Consider also rejecting duplicate in-flight `MessageID`s from the same sender, similar to the duplicate-request-ID protections already implemented in the v2 HTTP trigger handler and the confidential relay handler. [4](#0-3) [5](#0-4) 

### Proof of Concept
1. An external, unauthenticated client sends repeated `web_api_trigger` legacy-format messages (each with a unique `MessageID` and a fresh `Timestamp` to pass the staleness check) to the Gateway's user-facing endpoint.
2. Each message reaches `HandleLegacyUserMessage`, passes the payload/timestamp checks, hits the `// TODO: apply allowlist and rate-limiting here` marker with no enforcement, and is forwarded via `don.SendToNode` to every member in `h.donConfig.Members`. [1](#0-0) 
3. Repeating this at high volume multiplies gateway-side load and node-directed traffic across the entire DON with no throttling gate, consistent with the flooding/DOS impact described in the SEDA report.

### Citations

**File:** core/services/gateway/handlers/capabilities/handler.go (L164-168)
```go
func (h *handler) handleWebAPIOutgoingMessage(ctx context.Context, msg *api.Message, nodeAddr string) error {
	h.lggr.Debugw("handling webAPI outgoing message", "messageId", msg.Body.MessageID, "nodeAddr", nodeAddr)
	if !h.nodeRateLimiter.Allow(nodeAddr) {
		return fmt.Errorf("rate limit exceeded for node %s", nodeAddr)
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L299-338)
```go
func (h *handler) pruneCallbacks() {
	h.mu.Lock()
	defer h.mu.Unlock()

	// First, remove expired callbacks.
	maxAge := time.Duration(h.config.CallbackMaxAgeSec) * time.Second
	now := time.Now()
	var expired int
	for id, cb := range h.savedCallbacks {
		if now.Sub(cb.createdAt) > maxAge {
			delete(h.savedCallbacks, id)
			expired++
		}
	}

	// If there are still too many callbacks, sort them by creation time and remove the oldest ones.
	maxSize := h.config.MaxSavedCallbacks
	var evicted int
	if len(h.savedCallbacks) > maxSize {
		type entry struct {
			id        string
			createdAt time.Time
		}
		entries := make([]entry, 0, len(h.savedCallbacks))
		for id, cb := range h.savedCallbacks {
			entries = append(entries, entry{id, cb.createdAt})
		}
		sort.Slice(entries, func(i, j int) bool {
			return entries[i].createdAt.Before(entries[j].createdAt)
		})
		// Trim to maxSize/2 to avoid sorting the list too frequently.
		for _, e := range entries[:len(entries)-maxSize/2] {
			delete(h.savedCallbacks, e.id)
			evicted++
		}
	}

	if expired > 0 || evicted > 0 {
		h.lggr.Infow("Pruned savedCallbacks", "expired", expired, "evicted", evicted, "remaining", len(h.savedCallbacks))
	}
```

**File:** core/services/gateway/handlers/capabilities/handler.go (L384-420)
```go
	// TODO: apply allowlist and rate-limiting here
	if msg.Body.Method != MethodWebAPITrigger {
		h.lggr.Errorw("unsupported method", "method", body.Method)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UnsupportedMethodError),
				"invalid method "+msg.Body.Method,
				nil,
			),
			ErrorCode: api.UnsupportedMethodError,
		})
	}
	req, err := common.ValidatedRequestFromMessage(msg)
	if err != nil {
		h.lggr.Errorw(ErrTransformingMessageToRequest)
		return callback.SendResponse(handlers.UserCallbackPayload{
			RawResponse: codec.EncodeNewErrorResponse(
				msg.Body.MessageID,
				api.ToJSONRPCErrorCode(api.UserMessageParseError),
				ErrTransformingMessageToRequest,
				nil,
			),
			ErrorCode: api.UserMessageParseError,
		})
	}

	h.mu.Lock()
	h.savedCallbacks[msg.Body.MessageID] = &savedCallback{id: msg.Body.MessageID, createdAt: time.Now(), Callback: callback}
	don := h.don
	h.mu.Unlock()

	// Send original request to all nodes
	for _, member := range h.donConfig.Members {
		err = errors.Join(err, don.SendToNode(ctx, member.Address, req))
	}
	return err
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L414-420)
```go
func (h *handler) newActiveRequest(req jsonrpc.Request[json.RawMessage], labels requestLabels, callback gwhandlers.Callback) (*activeRequest, error) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.activeRequests[req.ID] != nil {
		h.lggr.Errorw("request id already exists", "requestID", req.ID, "executionID", labels.ExecutionID)
		return nil, errors.New("request ID already exists: " + req.ID)
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler_test.go (L320-353)
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
```
