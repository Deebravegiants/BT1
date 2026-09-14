### Title
Confidential relay gateway silently drops node responses on rate-limit, permanently losing that node's vote and enabling cross-user quorum-starvation DoS - (File: `core/services/gateway/handlers/confidentialrelay/handler.go`)

### Summary
`HandleNodeMessage` in the confidential relay gateway handler drops an incoming node response with no retry and no re-queue whenever the shared per-node or global rate limiter is exceeded at the moment that response arrives, exactly mirroring the reported bug class: a resource check that fails "at the moment of processing" causes the item to be silently skipped forever rather than retried. Because these rate limiters are shared across all concurrent user requests handled by the DON, an unprivileged caller can exhaust a node's token bucket to make that node's *legitimate* response for a different, concurrently-active user request get dropped.

### Finding Description
`HandleNodeMessage` checks `nodeRateLimiter.Allow(ctx)` and `h.globalNodeRateLimiter.Allow(ctx)` before recording a node's response, and if either is exceeded it just logs and returns `nil`, discarding the response entirely: [1](#0-0) 

The rate limiters (`perNodeRateLimiters`, `globalNodeRateLimiter`) are created once per handler/DON and shared across every `activeRequest` the gateway is currently tracking: [2](#0-1) 

Unlike the trigger handler's node dispatch (`sendToShard`), which retries failed sends with backoff, there is no compensating mechanism here: once a node's response for a given `req.ID` is dropped by the rate limiter, it is gone — `addResponseForNode` is the only place a response is ever recorded, and it is never invoked again for that (node, requestID) pair. The request then depends on `removeExpiredRequests`/`forwardGracedRequests` to eventually resolve with whatever partial bundle was collected, or time out: [3](#0-2) 

The existing test `TestConfidentialRelayHandler_RateLimitedNode` explicitly documents this "silently dropped" behavior and shows the affected callback simply times out with no response delivered: [4](#0-3) 

Because the limiter is keyed only by `nodeAddr` (not by request or by caller), any unprivileged user who can submit `HandleJSONRPCUserMessage` requests routed to this handler (`MethodSecretsGet`, `MethodCapabilityExec`) can burst enough traffic that a given node's responses to *other, unrelated* users' in-flight requests get dropped at exactly the moment they arrive. This is the analog to the VUSD bug: a resource-availability check ("is there rate-limit budget left / is there enough balance") performed at processing time causes the unit of work (a withdrawal, a node's signed response) to be permanently skipped instead of retried or queued, and an adversary can trigger the failing condition on demand to grief other users.

### Impact Explanation
A dropped response reduces the number of signed responses `forwardBundleOrTerminateIfReady` can ever see for that request (`maxPossibleSigned = summary.Signed() + remaining` only counts nodes that haven't yet answered — a rate-limited-and-dropped answer is neither "signed" nor still "remaining" in a useful sense once the true response is discarded and the node doesn't resend). If enough responses for a given request are dropped this way, the request can fall below `minQuorum` (F+1) and get a hard failure (`api.FatalError`/timeout) instead of succeeding, denying service to the *victim* user even though the DON actually answered correctly. This is triggerable by an unprivileged party (anyone able to submit relay requests) against arbitrary concurrent users sharing the same DON member, i.e., a cross-user, request-level DoS analogous to the VUSD "withdrawal silently skipped, never retried" issue.

### Likelihood Explanation
Likelihood is limited by needing enough concurrent request volume to line up a victim's node response with an attacker-induced rate-limit exhaustion window, and by the presence of `RequestTimeoutSec`/quorum-grace fallbacks that let many requests still succeed on a partial bundle. It is not a guaranteed 100%-reliable griefing primitive like the original front-running scenario, but it is a real, reachable defect: the rate limiter drop path has zero retry/backoff, unlike every other node-fan-out path in this codebase (e.g. `sendToShard` in the HTTP trigger handler), which was clearly designed with retries specifically to avoid this class of bug.

### Recommendation
- Do not silently discard a node's response when the per-node/global rate limiter trips; either queue it for later processing once budget is available, or explicitly request the node to resend/retry.
- Alternatively, scope the shared token buckets so that a single burst from one workflow/request cannot cause a different active request's node response to be dropped (e.g., account for consumption before generating outbound load rather than gating inbound response processing).
- At minimum, log at Warn/Error and increment a metric distinguishing "response dropped due to rate limit" from a genuine node failure, and consider excluding the dropped node from the `remaining` calculation so quorum math doesn't optimistically assume it may still answer.

### Proof of Concept
1. Configure `GatewayConfidentialRelayPerNodeRate` with a small burst (as in `TestConfidentialRelayHandler_RateLimitedNode`, `perNodeRateLimiters[nodeOne.Address] = limits.GlobalRateLimiter(rate.Limit(0.001), 1)`).
2. User A submits request 1 (`HandleJSONRPCUserMessage`); node responds and consumes the node's rate-limit burst token via `HandleNodeMessage`.
3. Before the token bucket refills, User B (unrelated, unprivileged) submits request 2 to the same DON; the same node sends back a legitimate signed response.
4. `HandleNodeMessage` calls `nodeRateLimiter.Allow(ctx)` for the node, which now returns `false`, so the function returns `nil` at line 448 without ever calling `ar.addResponseForNode` — User B's node response is lost.
5. If this repeats across enough nodes for User B's request, `forwardBundleOrTerminateIfReady` cannot reach quorum, and User B's request eventually fails/times out via `removeExpiredRequests`, even though the DON actually answered correctly. [5](#0-4)

### Citations

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L268-275)
```go
	perNodeRateLimiters := make(map[string]limits.RateLimiter, len(donConfig.Members))
	for _, member := range donConfig.Members {
		rl, makeErr := limitsFactory.MakeRateLimiter(cresettings.Default.GatewayConfidentialRelayPerNodeRate)
		if makeErr != nil {
			return nil, fmt.Errorf("failed to create per-node rate limiter for %s: %w", member.Address, makeErr)
		}
		perNodeRateLimiters[member.Address] = rl
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L337-369)
```go
func (h *handler) removeExpiredRequests(ctx context.Context) {
	h.mu.RLock()
	var expiredRequests []*activeRequest
	now := h.clock.Now()
	for _, userRequest := range h.activeRequests {
		if now.Sub(userRequest.createdAt) > h.requestTimeout {
			expiredRequests = append(expiredRequests, userRequest)
		}
	}
	h.mu.RUnlock()

	for _, er := range expiredRequests {
		responses := er.copiedResponses()
		l := h.requestLogger(er.req, er.labels)
		l.Debugw("request expired, evaluating collected relay responses",
			"collected", len(responses),
			"nodes", len(h.donConfig.Members),
			"unanswered", len(h.donConfig.Members)-len(responses),
		)
		summary, err := h.bundler.Bundle(er.req, responses, l)
		if err != nil {
			l.Errorw("failed to build relay response bundle", "error", err)
			if sendErr := h.sendResponseAndClearRequest(ctx, er, h.constructErrorResponse(er.req, api.FatalError, err)); sendErr != nil {
				l.Errorw("error returning bundle failure on expiry", "error", sendErr)
			}
			continue
		}
		// Expiry makes further responses unavailable to this request. The common
		// readiness path forwards a viable partial bundle or returns a timeout.
		if err := h.forwardBundleOrTerminateIfReady(ctx, l, er, summary, 0, true); err != nil {
			l.Errorw("error forwarding bundle on expiry", "error", err)
		}
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler.go (L438-453)
```go
func (h *handler) HandleNodeMessage(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	l := logger.With(h.lggr, "method", resp.Method, "requestID", resp.ID, "nodeAddr", nodeAddr)
	l.Debugw("handling node response")

	nodeRateLimiter, ok := h.perNodeRateLimiters[nodeAddr]
	if !ok {
		return fmt.Errorf("received message from unexpected node %s", nodeAddr)
	}
	if !nodeRateLimiter.Allow(ctx) {
		l.Debugw("node is rate limited", "nodeAddr", nodeAddr)
		return nil
	}
	if !h.globalNodeRateLimiter.Allow(ctx) {
		l.Debug("global relay rate limit exceeded")
		return nil
	}
```

**File:** core/services/gateway/handlers/confidentialrelay/handler_test.go (L883-965)
```go
func TestConfidentialRelayHandler_RateLimitedNode(t *testing.T) {
	t.Parallel()
	handlerConfig := Config{
		RequestTimeoutSec: 30,
	}
	methodConfig, err := json.Marshal(handlerConfig)
	require.NoError(t, err)

	lggr := logger.Test(t)
	don := mocks.NewDON(t)
	// F=0 so the forward threshold (2F+1) is 1: a single response from the one-node
	// DON forwards immediately, isolating the rate-limit behavior under test.
	donConfig := &config.DONConfig{
		DonID:   "test_relay_don",
		F:       0,
		Members: []config.NodeConfig{nodeOne},
	}
	clock := clockwork.NewFakeClock()
	limitsFactory := limits.Factory{Settings: cresettings.DefaultGetter, Logger: lggr}
	h, err := NewHandler(methodConfig, donConfig, don, lggr, clock, limitsFactory)
	require.NoError(t, err)
	h.globalNodeRateLimiter = limits.GlobalRateLimiter(rate.Limit(100), 100)
	h.perNodeRateLimiters[nodeOne.Address] = limits.GlobalRateLimiter(rate.Limit(0.001), 1)

	don.On("SendToNode", mock.Anything, mock.Anything, mock.Anything).Return(nil)

	cb := common.NewCallback()
	params := json.RawMessage(`{"workflow_id":"wf1"}`)
	req := jsonrpc.Request[json.RawMessage]{
		ID:     "req-ratelimit",
		Method: MethodCapabilityExec,
		Params: &params,
	}

	err = h.HandleJSONRPCUserMessage(t.Context(), req, cb)
	require.NoError(t, err)

	resultData := json.RawMessage(`{"result":{"payload":"r"},"signature":{}}`)
	response := jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      "req-ratelimit",
		Method:  MethodCapabilityExec,
		Result:  &resultData,
	}

	// First response from node uses the burst allowance
	err = h.HandleNodeMessage(t.Context(), &response, nodeOne.Address)
	require.NoError(t, err)

	// Verify callback was called
	ctx, cancel := context.WithTimeout(t.Context(), 100*time.Millisecond)
	defer cancel()
	resp, err := cb.Wait(ctx)
	require.NoError(t, err)
	assert.Equal(t, api.NoError, resp.ErrorCode)

	// Start a new request
	cb2 := common.NewCallback()
	req2 := jsonrpc.Request[json.RawMessage]{
		ID:     "req-ratelimit-2",
		Method: MethodCapabilityExec,
		Params: &params,
	}
	err = h.HandleJSONRPCUserMessage(t.Context(), req2, cb2)
	require.NoError(t, err)

	response2 := jsonrpc.Response[json.RawMessage]{
		Version: jsonrpc.JsonRpcVersion,
		ID:      "req-ratelimit-2",
		Method:  MethodCapabilityExec,
		Result:  &resultData,
	}

	// Second response should be rate limited (silently dropped)
	err = h.HandleNodeMessage(t.Context(), &response2, nodeOne.Address)
	require.NoError(t, err)

	// Callback should NOT be called - verify with timeout
	ctx2, cancel2 := context.WithTimeout(t.Context(), 50*time.Millisecond)
	defer cancel2()
	_, err = cb2.Wait(ctx2)
	require.Error(t, err) // Should timeout
}
```
