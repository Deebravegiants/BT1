Audit Report

## Title
Stale/late node trigger responses can be misdelivered to an unrelated, reused request ID, causing cross-user response confusion in the gateway HTTP trigger handler - (File: `core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go`)

## Summary
`setupCallback` only rejects a `requestID` while it exists in `h.callbacks`, and `reapExpiredCallbacks` deletes unprocessed entries after `CleanUpPeriodMs` elapses without ever notifying the original caller of failure, freeing the ID for reuse. `HandleNodeTriggerResponse` then matches incoming node responses purely by the `resp.ID` string against whatever entry currently occupies that key in `h.callbacks`, with no execution nonce or workflow/owner binding to the actual originating request. If a slow node's response for a reaped request arrives after a new, unrelated request has reused the same ID and is served by an overlapping shard, the stale response is fed into the new request's aggregator and — if quorum is reached — delivered to the new caller as their result.

## Finding Description
The vulnerable chain is present exactly as described in the code:

- `setupCallback` checks only presence in the live map, not any tombstone/expiry history: [1](#0-0) 
- `reapExpiredCallbacks` deletes unprocessed entries purely based on age and only increments a metric — it never calls `handleUserError` or otherwise notifies the original caller: [2](#0-1)  and `cleanupCallback` closes `doneCh` and deletes the map entry unconditionally: [3](#0-2) 
- `HandleNodeTriggerResponse` looks the response up strictly by `resp.ID` in the live map, and validates only that the sending node's shard has an aggregator registered under that ID — it does not check that the aggregator/callback belongs to the workflow/owner that actually produced this `resp.ID` originally: [4](#0-3) 
- Once routed, `CollectAndAggregate` and `SendResponse` proceed to deliver the aggregated result to whoever's callback is currently registered under that ID: [5](#0-4) 

The routing dispatcher confirms that any node message ID without a "/" (i.e., a bare user-supplied `requestID`) is treated as a trigger response and routed to `HandleNodeTriggerResponse` regardless of which execution actually produced it: [6](#0-5) 

Default configuration values make the timing window plausible: `MaxTriggerRequestDurationMs` defaults to 1 minute (governing only the gateway's outbound retry loop to nodes) while `CleanUpPeriodMs` defaults to 10 minutes (governing callback reaping) — a genuinely slow node is not otherwise prevented from delivering a response well after the callback is reaped: [7](#0-6) 

No existing check reconciles a late response's originating workflow/owner against the current holder of the reused `requestID`; the only correlation performed is the shard/donID membership check, which is a property of deployment topology, not request identity.

## Impact Explanation
This matches the "cross-user response corruption" impact category. A client can receive workflow-execution output belonging to a completely unrelated execution — potentially from a different workflow owner — misapplied to their own request. This is a concrete confidentiality/integrity issue: the victim client acts on data it never requested, and the original caller's data may leak to an unintended recipient.

## Likelihood Explanation
Exploitation requires only unprivileged, internet-facing gateway API calls: (1) submit a request with `id=X` and allow it to go unanswered long enough to be reaped (fully attacker-controlled, e.g., by choosing an `id` and workflow known to have slow/degraded nodes, or simply waiting out `CleanUpPeriodMs`), (2) submit a second request reusing `id=X` for a different workflow assigned to an overlapping shard, and (3) rely on the first request's slow nodes eventually delivering their response. `requestID` is fully user-supplied with no built-in uniqueness enforcement beyond transient in-flight tracking, so conditions (1) and (2) are trivially engineered by any caller; condition (3) depends on deployment topology (shard overlap) but is realistic in deployments with a limited number of DONs serving many workflows.

## Recommendation
- Track a reap tombstone (e.g., keep reaped IDs recorded for at least the maximum plausible late-response window) so `setupCallback` can still reject/rename reused IDs, or bind response correlation to a non-reusable composite key (`requestID` + execution nonce/workflowID) rather than the raw string ID alone.
- In `HandleNodeTriggerResponse`, validate that the node's response corresponds to the same workflow/execution context recorded when the callback was created, not just that the shard has a registered aggregator.
- On reap of an unprocessed callback, send a definitive timeout/error response to the original caller (via `handleUserError`) instead of merely incrementing a metric, closing the "silent failure" gap that enables ID reuse timing games.

## Proof of Concept
1. Client sends `workflows.execute` with `id="X"` for `workflowID=W1` assigned to shard `D`, with slow-responding nodes in `D`.
2. Wait for `CleanUpPeriodMs` to elapse without quorum; `reapExpiredCallbacks` deletes the entry for `id="X"` silently (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:561-581`).
3. Immediately send a new `workflows.execute` request also using `id="X"`, for `workflowID=W2` also assigned to shard `D`; `setupCallback` accepts it since no conflicting entry exists (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:419-426`).
4. Deliver (or simulate, via a controlled/slow node) the stale W1 node responses for `id="X"` from shard `D`; `HandleNodeTriggerResponse` matches them to the new W2 callback entry and, once quorum is reached, calls `saved.SendResponse` delivering the stale W1 result to the W2 caller (`core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go:474-530`).
5. A Go unit/integration test extending `http_trigger_handler_test.go` can simulate this by directly invoking `setupCallback`/`cleanupCallback`/`HandleNodeTriggerResponse` in this sequence to assert that a callback registered for `W2` receives an aggregated response built from responses tagged with `id="X"` that were originally sent for `W1`.

### Citations

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

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L463-472)
```go
func (h *httpTriggerHandler) cleanupCallback(requestID string) {
	saved, exists := h.callbacks[requestID]
	if !exists {
		return
	}
	if !saved.processed {
		close(saved.doneCh)
	}
	delete(h.callbacks, requestID)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L474-497)
```go
func (h *httpTriggerHandler) HandleNodeTriggerResponse(ctx context.Context, resp *jsonrpc.Response[json.RawMessage], nodeAddr string) error {
	h.lggr.Debugw("handling trigger response", "requestID", resp.ID, "nodeAddr", nodeAddr, "error", resp.Error, "result", resp.Result)
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	saved, exists := h.callbacks[resp.ID]
	if !exists {
		return errors.New("callback not found for request ID: " + resp.ID)
	}
	if saved.processed {
		h.lggr.Debugw("request already processed, ignoring late response", "requestID", resp.ID, "nodeAddr", nodeAddr)
		return nil
	}

	// Route the response into the aggregator for the shard that owns this node.
	shard, ok := h.nodeAddrToShard[nodeAddr]
	if !ok {
		return fmt.Errorf("received trigger response from unknown node %s (no owning shard)", nodeAddr)
	}
	agg, ok := saved.responseAggregators[shard.donID]
	if !ok {
		// The node belongs to a shard this workflow isn't assigned to (or the
		// callback was captured before the workflow was assigned there).
		return fmt.Errorf("node %s (shard %s) is not assigned to workflow for request ID %s", nodeAddr, shard.donID, resp.ID)
	}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L498-530)
```go
	aggResp, err := agg.CollectAndAggregate(resp, nodeAddr)
	if err != nil {
		return err
	}
	if aggResp == nil {
		h.lggr.Debugw("Not enough responses to aggregate", "requestID", resp.ID, "nodeAddress", nodeAddr, "shard", shard.donID)
		return nil
	}
	rawResp, err := json.Marshal(aggResp)
	if err != nil {
		return errors.New("failed to marshal response: " + err.Error())
	}

	err = saved.SendResponse(handlers.UserCallbackPayload{
		RawResponse: rawResp,
		ErrorCode:   api.NoError,
	})
	if err != nil {
		return err
	}

	// First shard to reach quorum wins: after successfully sending the response,
	// mark the callback as processed and close doneCh, stopping all shard sends.
	// The entry is kept in the map so late responses are recognized as such and
	// is removed later by the periodic reaper.
	saved.processed = true
	close(saved.doneCh)
	h.callbacks[resp.ID] = saved
	latencyMs := time.Since(saved.requestStartTime).Milliseconds()
	h.metrics.RecordRequestHandlerLatency(ctx, latencyMs, h.lggr)
	h.metrics.IncrementRequestSuccess(ctx, h.lggr)
	h.lggr.Debugw("Sent response to user", "requestID", resp.ID, "latencyMs", latencyMs)
	return nil
```

**File:** core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go (L561-581)
```go
// reapExpiredCallbacks removes callbacks that are older than the maximum age
func (h *httpTriggerHandler) reapExpiredCallbacks(ctx context.Context) {
	h.callbacksMu.Lock()
	defer h.callbacksMu.Unlock()
	now := time.Now()
	var expiredCount int
	for reqID, callback := range h.callbacks {
		if now.Sub(callback.createdAt) > time.Duration(h.config.CleanUpPeriodMs)*time.Millisecond {
			if !callback.processed {
				h.metrics.IncrementRequestErrors(ctx, jsonrpc.ErrInternal, h.lggr)
			}
			h.cleanupCallback(reqID)
			expiredCount++
		}
	}
	if expiredCount > 0 {
		h.metrics.IncrementPendingRequestsCleanUpCount(ctx, int64(expiredCount), h.lggr)
		h.lggr.Infow("Removed expired callbacks", "count", expiredCount, "remaining", len(h.callbacks))
	}
	h.metrics.RecordPendingRequestsCount(ctx, int64(len(h.callbacks)), h.lggr)
}
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L31-33)
```go
	defaultCleanUpPeriodMs               = 1000 * 60 * 10 // 10 minutes
	defaultMaxTriggerRequestDurationMs   = 1000 * 60      // 1 minute
	defaultNodeSendTimeoutMs             = 1000 * 10      // 10 seconds
```

**File:** core/services/gateway/handlers/capabilities/v2/http_handler.go (L256-295)
```go
	// Node messages follow the format "<methodName>/<workflowID>/<uuid>" or
	// "<methodName>/<workflowID>/<workflowExecutionID>/<uuid>". Messages are routed
	// based on the method in the ID.
	// Any messages without "/" is assumed to be a trigger response to a prior user request.
	if strings.Contains(resp.ID, "/") {
		if resp.Result == nil {
			h.lggr.Errorw("received response with empty result from node", "nodeAddr", nodeAddr, "error", resp.Error)
			return fmt.Errorf("received response with empty result from node %s", nodeAddr)
		}
		parts := strings.Split(resp.ID, "/")
		methodName := parts[0]
		switch methodName {
		case gateway_common.MethodHTTPAction:
			start := time.Now()
			h.metrics.IncrementActionRequestCount(ctx, nodeAddr, h.lggr)
			err := h.makeOutgoingRequest(ctx, resp, nodeAddr)
			if err != nil {
				h.metrics.IncrementActionRequestFailures(ctx, nodeAddr, h.lggr)
			}
			h.metrics.RecordActionRequestLatency(ctx, time.Since(start).Milliseconds(), h.lggr)
			return err
		case gateway_common.MethodPushWorkflowMetadata:
			h.metrics.IncrementMetadataRequestCount(ctx, nodeAddr, gateway_common.MethodPushWorkflowMetadata, h.lggr)
			err := h.metadataHandler.OnMetadataPush(ctx, resp, nodeAddr)
			if err != nil {
				h.metrics.IncrementMetadataProcessingFailures(ctx, nodeAddr, gateway_common.MethodPushWorkflowMetadata, h.lggr)
			}
			return err
		case gateway_common.MethodPullWorkflowMetadata:
			h.metrics.IncrementMetadataRequestCount(ctx, nodeAddr, gateway_common.MethodPullWorkflowMetadata, h.lggr)
			err := h.metadataHandler.OnMetadataPullResponse(ctx, resp, nodeAddr)
			if err != nil {
				h.metrics.IncrementMetadataProcessingFailures(ctx, nodeAddr, gateway_common.MethodPullWorkflowMetadata, h.lggr)
			}
			return err
		default:
			return fmt.Errorf("unsupported method %s in node message ID %s", methodName, resp.ID)
		}
	}
	return h.triggerHandler.HandleNodeTriggerResponse(ctx, resp, nodeAddr)
```
